"""
Enhanced reporting utilities for detailed threat analysis.

Provides line-by-line analysis showing exactly what triggered detection.
"""
from typing import List, Dict, Any
import re


class ThreatReport:
    """Detailed threat report for a single document."""
    
    def __init__(self, scan_result, file_content: str = None):
        self.doc_id = scan_result.doc_id
        self.risk = scan_result.risk
        self.quarantine = scan_result.quarantine
        self.reasons = scan_result.reasons
        self.signals = scan_result.signals
        self.file_content = file_content
        
    def get_detailed_report(self) -> Dict[str, Any]:
        """
        Generate detailed report with line-level analysis.
        
        Returns:
            Dict with detailed threat information
        """
        report = {
            'file': self.doc_id,
            'risk_score': self.risk,
            'status': 'QUARANTINED' if self.quarantine else 'SAFE',
            'overall_verdict': self._get_verdict(),
            'detection_reasons': self.reasons,
            'threat_lines': [],
            'statistics': {
                'total_lines': 0,
                'suspicious_lines': 0,
                'heuristic_score': self.signals.heuristic,
                'embedding_score': self.signals.embedding
            }
        }
        
        # Analyze line by line if content available
        if self.file_content:
            threat_lines = self._analyze_lines()
            report['threat_lines'] = threat_lines
            report['statistics']['total_lines'] = len(self.file_content.splitlines())
            report['statistics']['suspicious_lines'] = len(threat_lines)
        
        return report
    
    def _get_verdict(self) -> str:
        """Get human-readable verdict."""
        if self.risk >= 90:
            return "CRITICAL THREAT - Immediate action required"
        elif self.risk >= 70:
            return "HIGH RISK - Should be quarantined"
        elif self.risk >= 50:
            return "MODERATE RISK - Review recommended"
        elif self.risk >= 30:
            return "LOW RISK - Potentially suspicious"
        else:
            return "SAFE - No threats detected"
    
    def _analyze_lines(self) -> List[Dict[str, Any]]:
        """
        Analyze content line by line to find suspicious patterns.
        
        Returns:
            List of dicts with line number, content, and reasons
        """
        threat_lines = []
        
        # Common threat patterns with explanations
        patterns = [
            {
                'pattern': r'ignore\s+(all\s+)?previous\s+instructions?',
                'reason': 'Prompt injection - attempts to override system instructions',
                'severity': 'HIGH'
            },
            {
                'pattern': r'disregard\s+(all\s+)?previous\s+(commands?|instructions?)',
                'reason': 'Prompt injection - attempts to bypass safety measures',
                'severity': 'HIGH'
            },
            {
                'pattern': r'reveal\s+(your\s+)?(secrets?|prompt|system)',
                'reason': 'Information extraction attack - attempts to leak system info',
                'severity': 'HIGH'
            },
            {
                'pattern': r'<script[^>]*>',
                'reason': 'Cross-site scripting (XSS) - malicious JavaScript code',
                'severity': 'CRITICAL'
            },
            {
                'pattern': r'javascript:',
                'reason': 'JavaScript injection - attempts to execute malicious code',
                'severity': 'HIGH'
            },
            {
                'pattern': r'(union|select|insert|delete|drop|update)\s+.*\s+(from|into|table)',
                'reason': 'SQL injection - attempts to manipulate database queries',
                'severity': 'CRITICAL'
            },
            {
                'pattern': r'<iframe[^>]*>',
                'reason': 'Iframe injection - can load malicious content',
                'severity': 'HIGH'
            },
            {
                'pattern': r'eval\s*\(',
                'reason': 'Code execution - attempts to execute arbitrary code',
                'severity': 'HIGH'
            },
            {
                'pattern': r'exec\s*\(',
                'reason': 'Code execution - attempts to execute system commands',
                'severity': 'HIGH'
            },
            {
                'pattern': r'__import__\s*\(',
                'reason': 'Dynamic import - can import malicious modules',
                'severity': 'MEDIUM'
            },
            {
                'pattern': r'(backdoor|trojan|malware)',
                'reason': 'Malware reference - explicitly mentions malicious software',
                'severity': 'CRITICAL'
            },
            {
                'pattern': r'jailbreak',
                'reason': 'Jailbreak attempt - tries to bypass safety constraints',
                'severity': 'HIGH'
            }
        ]
        
        lines = self.file_content.splitlines()
        
        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()
            matched_patterns = []
            
            # Check each pattern
            for pattern_info in patterns:
                if re.search(pattern_info['pattern'], line_lower, re.IGNORECASE):
                    matched_patterns.append({
                        'reason': pattern_info['reason'],
                        'severity': pattern_info['severity']
                    })
            
            # If any patterns matched, add to threat lines
            if matched_patterns:
                threat_lines.append({
                    'line_number': line_num,
                    'content': line.strip(),
                    'threats': matched_patterns,
                    'severity': max(p['severity'] for p in matched_patterns)
                })
        
        return threat_lines
    
    def print_report(self):
        """Print formatted report to console."""
        report = self.get_detailed_report()
        
        print("\n" + "=" * 80)
        print(f"📄 FILE: {report['file']}")
        print("=" * 80)
        print(f"Risk Score: {report['risk_score']}/100")
        print(f"Status: {report['status']}")
        print(f"Verdict: {report['overall_verdict']}")
        print()
        
        if report['detection_reasons']:
            print("🔍 DETECTION REASONS:")
            for reason in report['detection_reasons']:
                print(f"  • {reason}")
            print()
        
        if report['threat_lines']:
            print("⚠️  SUSPICIOUS LINES DETECTED:")
            print("-" * 80)
            for threat in report['threat_lines']:
                print(f"\nLine {threat['line_number']}: [{threat['severity']}]")
                print(f"  Content: {threat['content'][:100]}...")
                print(f"  Threats:")
                for t in threat['threats']:
                    print(f"    • {t['reason']} ({t['severity']})")
            print("-" * 80)
        
        print(f"\n📊 STATISTICS:")
        print(f"  Total lines: {report['statistics']['total_lines']}")
        print(f"  Suspicious lines: {report['statistics']['suspicious_lines']}")
        print(f"  Heuristic score: {report['statistics']['heuristic_score']:.2f}")
        print(f"  Embedding score: {report['statistics']['embedding_score']:.2f}")
        print("=" * 80)


def generate_batch_report(results: list, files: list = None) -> Dict[str, Any]:
    """
    Generate comprehensive report for multiple files.
    
    Args:
        results: List of ScanResult objects
        files: Optional list of file info dicts with content
        
    Returns:
        Comprehensive report dictionary
    """
    # Create detailed reports for each file
    detailed_reports = []
    
    for i, result in enumerate(results):
        content = None
        if files and i < len(files):
            content = files[i].get('content')
        
        threat_report = ThreatReport(result, content)
        detailed_reports.append(threat_report.get_detailed_report())
    
    # Calculate overall statistics
    total_files = len(results)
    quarantined = sum(1 for r in results if r.quarantine)
    safe = total_files - quarantined
    avg_risk = sum(r.risk for r in results) / total_files if results else 0
    
    # Get critical threats
    critical_threats = [
        r for r in detailed_reports
        if r['risk_score'] >= 90
    ]
    
    # Get high risk threats
    high_risk_threats = [
        r for r in detailed_reports
        if 70 <= r['risk_score'] < 90
    ]
    
    return {
        'summary': {
            'total_files': total_files,
            'safe_files': safe,
            'quarantined_files': quarantined,
            'critical_threats': len(critical_threats),
            'high_risk_threats': len(high_risk_threats),
            'average_risk_score': round(avg_risk, 2)
        },
        'detailed_reports': detailed_reports,
        'critical_files': [r['file'] for r in critical_threats],
        'high_risk_files': [r['file'] for r in high_risk_threats],
        'safe_files': [r['file'] for r in detailed_reports if r['status'] == 'SAFE']
    }


def save_report_to_html(report: Dict[str, Any], output_file: str):
    """
    Save report as formatted HTML file.
    
    Args:
        report: Report dictionary from generate_batch_report
        output_file: Output HTML file path
    """
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SentinelDF Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .summary {{ background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #333; }}
        .file-report {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }}
        .safe {{ border-left: 5px solid #4CAF50; }}
        .warning {{ border-left: 5px solid #ff9800; }}
        .danger {{ border-left: 5px solid #f44336; }}
        .threat-line {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 3px solid #ff9800; }}
        .severity-critical {{ color: #d32f2f; font-weight: bold; }}
        .severity-high {{ color: #f57c00; font-weight: bold; }}
        .severity-medium {{ color: #fbc02d; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ SentinelDF Security Scan Report</h1>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="stat">
                <div class="stat-label">Total Files</div>
                <div class="stat-value">{report['summary']['total_files']}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Safe Files</div>
                <div class="stat-value" style="color: #4CAF50;">{report['summary']['safe_files']}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Quarantined</div>
                <div class="stat-value" style="color: #f44336;">{report['summary']['quarantined_files']}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Avg Risk</div>
                <div class="stat-value">{report['summary']['average_risk_score']}/100</div>
            </div>
        </div>
        
        <h2>📄 Detailed Results</h2>
"""
    
    for file_report in report['detailed_reports']:
        status_class = 'safe' if file_report['status'] == 'SAFE' else 'danger'
        
        html += f"""
        <div class="file-report {status_class}">
            <h3>{file_report['file']}</h3>
            <p><strong>Status:</strong> {file_report['status']}</p>
            <p><strong>Risk Score:</strong> {file_report['risk_score']}/100</p>
            <p><strong>Verdict:</strong> {file_report['overall_verdict']}</p>
"""
        
        if file_report['detection_reasons']:
            html += "<p><strong>Detection Reasons:</strong></p><ul>"
            for reason in file_report['detection_reasons']:
                html += f"<li>{reason}</li>"
            html += "</ul>"
        
        if file_report['threat_lines']:
            html += "<p><strong>⚠️ Suspicious Lines:</strong></p>"
            for threat in file_report['threat_lines']:
                html += f"""
                <div class="threat-line">
                    <p><strong>Line {threat['line_number']}:</strong> <span class="severity-{threat['severity'].lower()}">[{threat['severity']}]</span></p>
                    <code>{threat['content'][:200]}</code>
                    <ul>
"""
                for t in threat['threats']:
                    html += f"<li>{t['reason']} ({t['severity']})</li>"
                html += "</ul></div>"
        
        html += "</div>"
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
