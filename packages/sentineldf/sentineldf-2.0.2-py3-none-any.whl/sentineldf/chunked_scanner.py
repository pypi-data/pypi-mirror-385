"""
Chunked document scanner for large files.
Handles Word docs, PDFs, and large text files by breaking them into chunks.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class ChunkedScanner:
    """Scanner that handles large documents by chunking."""
    
    def __init__(self, client, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize chunked scanner.
        
        Args:
            client: SentinelDF client instance
            chunk_size: Words per chunk (default: 1000)
            overlap: Overlapping words between chunks (default: 200)
        """
        self.client = client
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_from_docx(self, file_path: str) -> str:
        """Extract text from Word document."""
        if DocxDocument is None:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        
        doc = DocxDocument(file_path)
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        return '\n'.join(text_parts)
    
    def extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")
        
        text_parts = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return '\n'.join(text_parts)
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension."""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext == '.docx':
            return self.extract_from_docx(str(file_path))
        elif ext == '.pdf':
            return self.extract_from_pdf(str(file_path))
        elif ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Returns:
            List of dicts with chunk info: {text, start_word, end_word}
        """
        words = text.split()
        chunks = []
        
        if len(words) <= self.chunk_size:
            # Small enough to scan as-is
            return [{
                'id': 0,
                'text': text,
                'start_word': 0,
                'end_word': len(words),
                'word_count': len(words)
            }]
        
        i = 0
        chunk_id = 0
        while i < len(words):
            end = min(i + self.chunk_size, len(words))
            chunk_words = words[i:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start_word': i,
                'end_word': end,
                'word_count': len(chunk_words)
            })
            
            chunk_id += 1
            i += self.chunk_size - self.overlap
        
        return chunks
    
    def scan_file(self, file_path: str, threshold: int = 50) -> Dict[str, Any]:
        """
        Scan a file using chunked approach.
        
        Args:
            file_path: Path to file
            threshold: Risk threshold for flagging chunks (default: 50)
            
        Returns:
            Dict with overall results and per-chunk details
        """
        # Extract text
        text = self.extract_text(file_path)
        
        # Chunk it
        chunks = self.chunk_text(text)
        
        # Scan each chunk
        chunk_results = []
        max_risk = 0
        total_quarantined = 0
        
        for chunk in chunks:
            response = self.client.scan([chunk['text']])
            result = response.results[0]
            
            chunk_result = {
                'chunk_id': chunk['id'],
                'start_word': chunk['start_word'],
                'end_word': chunk['end_word'],
                'risk': result.risk,
                'quarantine': result.quarantine,
                'reasons': result.reasons,
                'signals': result.signals
            }
            
            chunk_results.append(chunk_result)
            
            if result.risk > max_risk:
                max_risk = result.risk
            
            if result.quarantine:
                total_quarantined += 1
        
        # Aggregate results
        return {
            'file': file_path,
            'total_chunks': len(chunks),
            'max_risk': max_risk,
            'chunks_quarantined': total_quarantined,
            'overall_quarantine': total_quarantined > 0,
            'chunk_results': chunk_results,
            'recommendation': self._get_recommendation(max_risk, total_quarantined, len(chunks))
        }
    
    def _get_recommendation(self, max_risk: int, quarantined: int, total: int) -> str:
        """Generate recommendation based on scan results."""
        if max_risk >= 70:
            return f"⚠️ HIGH RISK: {quarantined}/{total} chunks quarantined. Review immediately."
        elif max_risk >= 50:
            return f"⚠️ MEDIUM RISK: Some suspicious content detected. Manual review recommended."
        elif max_risk >= 30:
            return f"ℹ️ LOW RISK: Minor concerns detected. Consider reviewing flagged sections."
        else:
            return f"✅ SAFE: No significant threats detected."
    
    def print_results(self, results: Dict[str, Any]):
        """Print scan results in readable format."""
        print(f"\n{'='*80}")
        print(f"📄 FILE: {results['file']}")
        print(f"{'='*80}")
        print(f"Total Chunks: {results['total_chunks']}")
        print(f"Max Risk: {results['max_risk']}/100")
        print(f"Quarantined Chunks: {results['chunks_quarantined']}")
        print(f"Overall Status: {'🚨 QUARANTINE' if results['overall_quarantine'] else '✅ SAFE'}")
        print(f"\n{results['recommendation']}")
        
        # Show high-risk chunks
        high_risk_chunks = [c for c in results['chunk_results'] if c['risk'] >= 50]
        if high_risk_chunks:
            print(f"\n⚠️ HIGH-RISK CHUNKS:")
            for chunk in high_risk_chunks:
                print(f"\n  Chunk {chunk['chunk_id']} (words {chunk['start_word']}-{chunk['end_word']})")
                print(f"  Risk: {chunk['risk']}/100")
                if chunk['reasons']:
                    print(f"  Reasons:")
                    for reason in chunk['reasons']:
                        print(f"    • {reason}")
        
        print(f"{'='*80}\n")


# Example usage
if __name__ == "__main__":
    from sentineldf import SentinelDF
    
    # Initialize
    client = SentinelDF(api_key="your_key_here")
    scanner = ChunkedScanner(client, chunk_size=1000, overlap=200)
    
    # Scan a large document
    results = scanner.scan_file("large_document.docx")
    scanner.print_results(results)
