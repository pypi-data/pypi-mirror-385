"""
Post-installation welcome message
"""

def show_welcome():
    """Display welcome message after installation."""
    welcome = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║  🎉 SentinelDF Successfully Installed!                            ║
║                                                                   ║
║  Data Firewall for LLM Training                                  ║
║  Version 2.0.0                                                   ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🚀 Quick Start                                                   ║
║  ─────────────                                                    ║
║                                                                   ║
║  1. Get your API key:                                            ║
║     https://sentineldf.com/dashboard                             ║
║                                                                   ║
║  2. Scan a file:                                                 ║
║     sentineldf scan-file your-data.txt --api-key YOUR_KEY        ║
║                                                                   ║
║  3. Scan a folder:                                               ║
║     sentineldf scan-folder ./data -r --api-key YOUR_KEY          ║
║                                                                   ║
║  4. Use in Python:                                               ║
║     from sentineldf import SentinelDF                            ║
║     client = SentinelDF(api_key="YOUR_KEY")                      ║
║     results = client.scan(["your text"])                         ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📚 Resources                                                     ║
║  ────────────                                                     ║
║                                                                   ║
║  • Documentation: https://docs.sentineldf.com                    ║
║  • Examples: https://github.com/varunsripad123/sentineldf        ║
║  • Support: support@sentineldf.com                               ║
║  • Dashboard: https://sentineldf.com/dashboard                   ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  💡 Features                                                      ║
║  ──────────                                                       ║
║                                                                   ║
║  ✓ Prompt injection detection                                    ║
║  ✓ Data poisoning detection                                      ║
║  ✓ Backdoor detection                                            ║
║  ✓ Batch folder scanning                                         ║
║  ✓ Detailed threat reports (HTML/JSON)                           ║
║  ✓ Command-line interface                                        ║
║  ✓ Python SDK                                                    ║
║                                                                   ║
║  Need help? Run: sentineldf --help                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(welcome)


if __name__ == '__main__':
    show_welcome()
