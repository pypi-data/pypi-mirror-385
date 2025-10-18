"""
SentinelDF Python SDK

Official Python client for the SentinelDF API.
"""
from .client import (
    SentinelDF,
    ScanResult,
    ScanSummary,
    UsageStats,
    ScanResponse,
    SentinelDFError,
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
)
from .file_utils import FileScanner, scan_and_analyze
from .reporting import ThreatReport, generate_batch_report, save_report_to_html

__version__ = "2.0.0"
__all__ = [
    "SentinelDF",
    "ScanResult",
    "ScanSummary",
    "UsageStats",
    "ScanResponse",
    "SentinelDFError",
    "AuthenticationError",
    "QuotaExceededError",
    "RateLimitError",
    "FileScanner",
    "scan_and_analyze",
    "ThreatReport",
    "generate_batch_report",
    "save_report_to_html",
]
