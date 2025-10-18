"""
SentinelDF Interactive GUI

Web-based interface for scanning files with drag-and-drop support,
real-time progress tracking, and interactive threat visualization.
"""
import os
import sys
import json
import webbrowser
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional
from flask import Flask, render_template, request, jsonify, send_file

from .client import SentinelDF, SentinelDFError
from .file_utils import FileScanner, scan_and_analyze
from .reporting import ThreatReport, generate_batch_report, save_report_to_html


# Flask app
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# Global state
client: Optional[SentinelDF] = None
scan_results = {}
scan_progress = {}


def create_gui_app(api_key: str, port: int = 5050):
    """Initialize the GUI with API key."""
    global client
    client = SentinelDF(api_key=api_key)
    return app


@app.route('/')
def index():
    """Main GUI page."""
    return render_template('index.html')


@app.route('/api/scan-files', methods=['POST'])
def scan_files():
    """Scan uploaded files."""
    if not client:
        return jsonify({'error': 'Not initialized'}), 500
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    scan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    scan_progress[scan_id] = {
        'total': len(files),
        'processed': 0,
        'status': 'scanning'
    }
    
    # Process files
    results = []
    texts = []
    doc_ids = []
    file_info = []
    
    for file in files:
        if file.filename:
            content = file.read().decode('utf-8', errors='ignore')
            texts.append(content)
            doc_ids.append(file.filename)
            file_info.append({
                'name': file.filename,
                'size': len(content)
            })
    
    try:
        # Scan with real API
        response = client.scan(texts, doc_ids=doc_ids)
        
        for i, result in enumerate(response.results):
            results.append({
                'doc_id': result.doc_id,
                'risk': result.risk,
                'quarantine': result.quarantine,
                'reasons': result.reasons,
                'action': result.action,
                'signals': result.signals,
                'file_info': file_info[i] if i < len(file_info) else {}
            })
        
        # Store results
        scan_results[scan_id] = {
            'results': results,
            'summary': {
                'total': len(results),
                'quarantined': sum(1 for r in results if r['quarantine']),
                'safe': sum(1 for r in results if not r['quarantine']),
                'avg_risk': sum(r['risk'] for r in results) / len(results) if results else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        scan_progress[scan_id]['status'] = 'complete'
        scan_progress[scan_id]['processed'] = len(files)
        
        return jsonify({
            'scan_id': scan_id,
            'results': results,
            'summary': scan_results[scan_id]['summary']
        })
        
    except SentinelDFError as e:
        scan_progress[scan_id]['status'] = 'error'
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-folder', methods=['POST'])
def scan_folder():
    """Scan a folder path."""
    if not client:
        return jsonify({'error': 'Not initialized'}), 500
    
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path or not os.path.exists(folder_path):
        return jsonify({'error': 'Invalid folder path'}), 400
    
    scan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    scan_progress[scan_id] = {
        'total': 0,
        'processed': 0,
        'status': 'scanning'
    }
    
    try:
        def progress_callback(processed, total):
            scan_progress[scan_id]['total'] = total
            scan_progress[scan_id]['processed'] = processed
        
        # Scan folder with real API
        result = scan_and_analyze(
            client,
            folder_path,
            recursive=True,
            progress_callback=progress_callback
        )
        
        # Convert results to dict format
        results = []
        for r in result['results']:
            results.append({
                'doc_id': r.doc_id,
                'risk': r.risk,
                'quarantine': r.quarantine,
                'reasons': r.reasons,
                'action': r.action,
                'signals': r.signals
            })
        
        scan_results[scan_id] = {
            'results': results,
            'summary': result['summary'],
            'timestamp': datetime.now().isoformat()
        }
        
        scan_progress[scan_id]['status'] = 'complete'
        
        return jsonify({
            'scan_id': scan_id,
            'results': results,
            'summary': result['summary']
        })
        
    except Exception as e:
        scan_progress[scan_id]['status'] = 'error'
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/<scan_id>')
def get_progress(scan_id):
    """Get scan progress."""
    if scan_id not in scan_progress:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify(scan_progress[scan_id])


@app.route('/api/results/<scan_id>')
def get_results(scan_id):
    """Get scan results."""
    if scan_id not in scan_results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify(scan_results[scan_id])


@app.route('/api/download-report/<scan_id>')
def download_report(scan_id):
    """Download HTML report."""
    if scan_id not in scan_results:
        return jsonify({'error': 'Results not found'}), 404
    
    data = scan_results[scan_id]
    
    # Generate HTML report
    report_path = f"/tmp/sentineldf_report_{scan_id}.html"
    
    # Convert to format expected by generate_batch_report
    from .client import ScanResult
    result_objects = []
    for r in data['results']:
        result_objects.append(ScanResult(
            doc_id=r['doc_id'],
            risk=r['risk'],
            quarantine=r['quarantine'],
            reasons=r['reasons'],
            action=r['action'],
            signals=r['signals']
        ))
    
    batch_report = generate_batch_report(result_objects)
    save_report_to_html(batch_report, report_path)
    
    return send_file(
        report_path,
        as_attachment=True,
        download_name=f'sentineldf_report_{scan_id}.html'
    )


@app.route('/api/download-json/<scan_id>')
def download_json(scan_id):
    """Download JSON report."""
    if scan_id not in scan_results:
        return jsonify({'error': 'Results not found'}), 404
    
    data = scan_results[scan_id]
    json_path = f"/tmp/sentineldf_report_{scan_id}.json"
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return send_file(
        json_path,
        as_attachment=True,
        download_name=f'sentineldf_report_{scan_id}.json'
    )


def launch_gui(api_key: str, port: int = 5050, auto_open: bool = True):
    """
    Launch the interactive GUI.
    
    Args:
        api_key: SentinelDF API key
        port: Port to run on (default: 5050)
        auto_open: Automatically open browser (default: True)
    """
    create_gui_app(api_key, port)
    
    url = f"http://localhost:{port}"
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 SentinelDF Interactive GUI                           ║
║                                                           ║
║   Running at: {url:<42} ║
║                                                           ║
║   Features:                                              ║
║   • Drag & Drop file uploads                            ║
║   • Real-time scanning progress                         ║
║   • Interactive threat visualization                    ║
║   • One-click report downloads                          ║
║   • Quarantine review interface                         ║
║                                                           ║
║   Press Ctrl+C to stop                                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if auto_open:
        # Open browser after short delay
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m sentineldf.gui YOUR_API_KEY")
        sys.exit(1)
    
    launch_gui(sys.argv[1])
