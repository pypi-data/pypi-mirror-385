"""
File and folder utilities for batch scanning.

Handles:
- Reading multiple file formats
- Recursive folder traversal
- Batch processing large datasets
- Progress tracking
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import mimetypes


class FileScanner:
    """Utilities for scanning files and folders."""
    
    # Supported text file extensions
    TEXT_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.jsx', '.ts', '.tsx',
        '.json', '.yaml', '.yml', '.xml', '.html', '.css',
        '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb',
        '.php', '.sh', '.bash', '.sql', '.r', '.scala',
        '.swift', '.kt', '.m', '.csv', '.log'
    }
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read a text file safely.
        
        Args:
            file_path: Path to file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File contents as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return None
        except Exception:
            return None
    
    @staticmethod
    def scan_folder(
        folder_path: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None,
        max_files: Optional[int] = None,
        max_file_size_mb: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scan a folder for text files.
        
        Args:
            folder_path: Path to folder
            recursive: Scan subfolders (default: True)
            extensions: List of extensions to include (e.g., ['.txt', '.py'])
            max_files: Maximum number of files to scan
            max_file_size_mb: Skip files larger than this (MB)
            
        Returns:
            List of dicts with file info: {path, content, size, extension}
        """
        if extensions is None:
            extensions = FileScanner.TEXT_EXTENSIONS
        else:
            extensions = set(ext.lower() for ext in extensions)
        
        max_size_bytes = max_file_size_mb * 1024 * 1024
        files = []
        
        # Use Path for cross-platform compatibility
        folder = Path(folder_path)
        
        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        
        # Get all files
        pattern = '**/*' if recursive else '*'
        
        for file_path in folder.glob(pattern):
            # Check limits
            if max_files and len(files) >= max_files:
                break
            
            # Skip directories
            if not file_path.is_file():
                continue
            
            # Check extension
            if file_path.suffix.lower() not in extensions:
                continue
            
            # Check file size
            try:
                file_size = file_path.stat().st_size
                if file_size > max_size_bytes:
                    continue
            except Exception:
                continue
            
            # Read content
            content = FileScanner.read_file(str(file_path))
            if content is None:
                continue
            
            files.append({
                'path': str(file_path),
                'content': content,
                'size': file_size,
                'extension': file_path.suffix,
                'name': file_path.name,
                'relative_path': str(file_path.relative_to(folder))
            })
        
        return files
    
    @staticmethod
    def scan_files(
        file_paths: List[str],
        max_file_size_mb: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scan specific files.
        
        Args:
            file_paths: List of file paths
            max_file_size_mb: Skip files larger than this
            
        Returns:
            List of file info dicts
        """
        max_size_bytes = max_file_size_mb * 1024 * 1024
        files = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if not path.exists() or not path.is_file():
                continue
            
            # Check size
            try:
                file_size = path.stat().st_size
                if file_size > max_size_bytes:
                    continue
            except Exception:
                continue
            
            # Read content
            content = FileScanner.read_file(str(path))
            if content is None:
                continue
            
            files.append({
                'path': str(path),
                'content': content,
                'size': file_size,
                'extension': path.suffix,
                'name': path.name
            })
        
        return files


def scan_and_analyze(
    client,
    folder_path: str,
    batch_size: int = 100,
    recursive: bool = True,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Scan a folder and analyze all files with SentinelDF.
    
    Args:
        client: SentinelDF client instance
        folder_path: Path to folder to scan
        batch_size: Files per batch (max 1000)
        recursive: Scan subfolders
        progress_callback: Function called with (processed, total)
        
    Returns:
        Dict with results and summary
    """
    # Scan folder for files
    files = FileScanner.scan_folder(
        folder_path,
        recursive=recursive,
        max_files=None  # Scan all
    )
    
    if not files:
        return {
            'results': [],
            'summary': {
                'total_files': 0,
                'scanned_files': 0,
                'quarantined_files': 0,
                'error': 'No files found'
            }
        }
    
    # Process in batches
    all_results = []
    total_files = len(files)
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        
        # Prepare documents for API
        texts = [f['content'] for f in batch]
        doc_ids = [f['relative_path'] if 'relative_path' in f else f['name'] for f in batch]
        metadata = [{'path': f['path'], 'size': f['size']} for f in batch]
        
        # Scan batch
        response = client.scan(
            texts=texts,
            doc_ids=doc_ids,
            metadata=metadata
        )
        
        all_results.extend(response.results)
        
        # Progress callback
        if progress_callback:
            progress_callback(min(i + batch_size, total_files), total_files)
    
    # Calculate overall summary
    quarantined = sum(1 for r in all_results if r.quarantine)
    
    return {
        'results': all_results,
        'summary': {
            'total_files': total_files,
            'scanned_files': len(all_results),
            'quarantined_files': quarantined,
            'safe_files': len(all_results) - quarantined,
            'avg_risk': sum(r.risk for r in all_results) / len(all_results) if all_results else 0
        }
    }
