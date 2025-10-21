import re
import os

REDACTION_TEXT = "[REDACTED]"

SENSITIVE_KEYS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "sensitive_keys.txt")
)


def load_sensitive_keys():
    """
    Load sensitive keys (like password, token) from file and precompile regex patterns.
    """
    patterns = []
    if not os.path.exists(SENSITIVE_KEYS_FILE):
        return patterns

    with open(SENSITIVE_KEYS_FILE, "r", encoding="utf-8") as f:
        keys = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for key in keys:
        escaped = re.escape(key)
        pattern = re.compile(rf"(?i)\b({escaped})\b\s*[:=\-]\s*([^,;\n]*)")
        patterns.append(pattern)

    return patterns


# Base key-based patterns
_KEY_PATTERNS = load_sensitive_keys()

# Extra heuristic patterns (independent of key names)
_HEURISTIC_PATTERNS = [
    # Emails
    re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    # Tokens or secrets (long random strings, e.g. abcd1234efgh5678)
    re.compile(r"\b[A-Za-z0-9_\-]{20,}\b"),
    # UUIDs
    re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"),
    # Credit cards
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    # JWTs (3 parts separated by dots)
    re.compile(r"\b[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\b"),
    # AWS Access Keys (AKIA...)
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]


def redact(message: str) -> str:
    """
    Replaces sensitive information in a log message with [REDACTED].
    Combines keyword-based and heuristic-based sanitization.
    """
    if not message or not isinstance(message, str):
        return message

    redacted = message

    # 1. Keyword-based replacements
    for pattern in _KEY_PATTERNS:
        redacted = pattern.sub(lambda m: f"{m.group(1)}={REDACTION_TEXT}", redacted)

    # 2. Heuristic-based replacements (value-only)
    for pattern in _HEURISTIC_PATTERNS:
        redacted = pattern.sub(REDACTION_TEXT, redacted)

    return redacted
