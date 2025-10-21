"""logguard - simple log redaction utilities

Version: 0.0.1 (prototype)
Contains:
- redact(text): high-performance redaction using regex and key lists
- RedactingFormatter: logging.Formatter that redacts record messages and args
- filter decorator: wraps functions to temporarily patch logging methods for safe logging
"""
__all__ = ["redact", "RedactingFormatter", "filter", "load_sensitive_keys"]

from .redactor import redact, load_sensitive_keys
from .handler import RedactingFormatter
from .decorator import filter
__version__ = "0.0.1"
