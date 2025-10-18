"""
SentinelDF Command-Line Interface

Scan files and folders for threats from the command line.
"""
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .client import SentinelDF, SentinelDFError
from .file_utils import FileScanner, scan_and_analyze
from .reporting import ThreatReport, generate_batch_report, save_report_to_html


def print_banner():
    """Print the SentinelDF banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗║
║   ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝║
║   ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ║
║   ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ║
║   ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗║
║   ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝║
║                                                           ║
║            Data Firewall for LLM Training                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def scan_text_command(args):
    """Scan a text string."""
    client = SentinelDF(api_key=args.api_key, base_url=args.base_url)
    
    try:
        response = client.scan([args.text])
        result = response.results[0]
        
        print("\n✓ Scan Complete!\n")
        print(f"Risk Score: {result.risk:.2f}")
        print(f"Status: {'🚨 QUARANTINED' if result.quarantine else '✅ SAFE'}")
        
        if result.reasons:
            print(f"\nReasons:")
            for reason in result.reasons:
                print(f"  • {reason}")
        
        if args.detailed:
            report = ThreatReport(result, args.text)
            report.print_report()
            
    except SentinelDFError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def scan_file_command(args):
    """Scan a single file."""
    client = SentinelDF(api_key=args.api_key, base_url=args.base_url)
    
    try:
        content = FileScanner.read_file(args.file)
        if content is None:
            print(f"❌ Could not read file: {args.file}", file=sys.stderr)
            sys.exit(1)
        
        response = client.scan([content], doc_ids=[args.file])
        result = response.results[0]
        
        print(f"\n✓ Scanned: {args.file}\n")
        print(f"Risk Score: {result.risk:.2f}")
        print(f"Status: {'🚨 QUARANTINED' if result.quarantine else '✅ SAFE'}")
        
        if result.reasons:
            print(f"\nReasons:")
            for reason in result.reasons:
                print(f"  • {reason}")
        
        if args.detailed:
            report = ThreatReport(result, content)
            report.print_report()
        
        if args.output:
            report = ThreatReport(result, content)
            detailed = report.get_detailed_report()
            
            if args.output.endswith('.html'):
                save_report_to_html(detailed, args.output)
                print(f"\n📄 Report saved to: {args.output}")
            else:
                with open(args.output, 'w') as f:
                    json.dump(detailed, f, indent=2)
                print(f"\n📄 Report saved to: {args.output}")
                
    except SentinelDFError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def scan_folder_command(args):
    """Scan a folder of files."""
    client = SentinelDF(api_key=args.api_key, base_url=args.base_url)
    
    try:
        print(f"\n🔍 Scanning folder: {args.folder}")
        print(f"Recursive: {args.recursive}")
        
        def progress_callback(processed, total):
            percent = (processed / total) * 100
            print(f"Progress: {processed}/{total} files ({percent:.1f}%)", end='\r')
        
        result = scan_and_analyze(
            client,
            args.folder,
            batch_size=args.batch_size,
            recursive=args.recursive,
            progress_callback=progress_callback if not args.quiet else None
        )
        
        summary = result['summary']
        
        print("\n\n✓ Scan Complete!\n")
        print(f"Total Files: {summary['total_files']}")
        print(f"Scanned: {summary['scanned_files']}")
        print(f"Safe: {summary.get('safe_files', 0)}")
        print(f"Quarantined: {summary['quarantined_files']} 🚨")
        print(f"Average Risk: {summary.get('avg_risk', 0):.2f}")
        
        if args.output:
            batch_report = generate_batch_report(
                result['results'],
                [{'path': r.doc_id} for r in result['results']]
            )
            
            if args.output.endswith('.html'):
                save_report_to_html(batch_report, args.output)
            else:
                with open(args.output, 'w') as f:
                    json.dump(batch_report, f, indent=2)
            
            print(f"\n📄 Full report saved to: {args.output}")
        
        if args.show_threats and summary['quarantined_files'] > 0:
            print("\n🚨 Quarantined Files:")
            for r in result['results']:
                if r.quarantine:
                    print(f"  • {r.doc_id} (Risk: {r.risk:.2f})")
                    
    except SentinelDFError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SentinelDF - Data Firewall for LLM Training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a text string
  sentineldf scan-text "Your text here" --api-key YOUR_KEY
  
  # Scan a single file
  sentineldf scan-file data.txt --api-key YOUR_KEY
  
  # Scan a folder
  sentineldf scan-folder ./data --api-key YOUR_KEY --output report.html
  
  # Scan with detailed report
  sentineldf scan-file data.txt --api-key YOUR_KEY --detailed
        """
    )
    
    # Global arguments
    parser.add_argument('--api-key', help='SentinelDF API key (or set SENTINELDF_API_KEY env var)')
    parser.add_argument('--base-url', default='https://api.sentineldf.com/v1', help='API base URL')
    parser.add_argument('--version', action='version', version='sentineldf-ai 2.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # scan-text command
    scan_text_parser = subparsers.add_parser('scan-text', help='Scan a text string')
    scan_text_parser.add_argument('text', help='Text to scan')
    scan_text_parser.add_argument('--detailed', action='store_true', help='Show detailed report')
    
    # scan-file command
    scan_file_parser = subparsers.add_parser('scan-file', help='Scan a file')
    scan_file_parser.add_argument('file', help='File path to scan')
    scan_file_parser.add_argument('--detailed', action='store_true', help='Show detailed report')
    scan_file_parser.add_argument('--output', '-o', help='Save report to file (.html or .json)')
    
    # scan-folder command
    scan_folder_parser = subparsers.add_parser('scan-folder', help='Scan a folder')
    scan_folder_parser.add_argument('folder', help='Folder path to scan')
    scan_folder_parser.add_argument('--recursive', '-r', action='store_true', default=True, help='Scan subfolders')
    scan_folder_parser.add_argument('--batch-size', type=int, default=100, help='Batch size (default: 100)')
    scan_folder_parser.add_argument('--output', '-o', help='Save report to file (.html or .json)')
    scan_folder_parser.add_argument('--show-threats', action='store_true', help='List all quarantined files')
    scan_folder_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    
    # gui command
    gui_parser = subparsers.add_parser('gui', help='Launch interactive GUI')
    gui_parser.add_argument('--port', type=int, default=5050, help='Port to run on (default: 5050)')
    gui_parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)
    
    # Check API key (except for GUI which prompts interactively)
    if args.command != 'gui':
        if not args.api_key:
            import os
            args.api_key = os.environ.get('SENTINELDF_API_KEY')
            if not args.api_key:
                print("\n❌ Error: API key required. Use --api-key or set SENTINELDF_API_KEY env var", file=sys.stderr)
                print("\nGet your API key at: https://sentineldf.com/dashboard\n")
                sys.exit(1)
    
    # Route to command handlers
    if args.command == 'scan-text':
        scan_text_command(args)
    elif args.command == 'scan-file':
        scan_file_command(args)
    elif args.command == 'scan-folder':
        scan_folder_command(args)
    elif args.command == 'gui':
        # Import GUI module
        from .gui import launch_gui
        
        # Get API key
        api_key = args.api_key
        if not api_key:
            import os
            api_key = os.environ.get('SENTINELDF_API_KEY')
        
        if not api_key:
            print("\n❌ Error: API key required for GUI")
            print("Set SENTINELDF_API_KEY environment variable or use --api-key\n")
            sys.exit(1)
        
        # Launch GUI
        launch_gui(api_key, port=args.port, auto_open=not args.no_browser)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
