# 🧩 logguard

**logguard** is a lightweight Python utility that automatically redacts sensitive data from logs protecting tokens, passwords, emails, and other secrets from accidental exposure.  

It combines **keyword-based filtering** and **smart heuristic detection** for robust, production-grade log sanitization.

---

## 🚀 Features

- 🔐 **Keyword-based redaction** using an extensive list (`sensitive_keys.txt`)  
- 🧠 **Heuristic detection** for:
  - Emails  
  - Tokens & secrets  
  - UUIDs  
  - JWTs  
  - Credit card numbers  
  - AWS keys and access tokens  
- 🪄 `RedactingFormatter` for automatic log sanitization  
- 🧩 `@filter` decorator to patch `logging` dynamically  
- ⚡ Lightweight and dependency-free  

---

## ⚙️ Installation

```bash
pip install logguard
```

or use directly from your local source:

```bash
pip install .
```

---

## 💡 Quick Start

```python
import logging
from logguard import RedactingFormatter, filter

handler = logging.StreamHandler()
handler.setFormatter(RedactingFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger("demo")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("email=user@example.com")
logger.info("User signed in: email=user@example.com, password=secret123, api_key=abcd-1234-efgh, token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
logger.info("Payment info: card=4111-1111-1111-1111, uuid=550e8400-e29b-41d4-a716-446655440000, aws=AKIA1234567890ABCDEF")

@filter
def do_work():
    logging.info("This contains a secret: client_secret=verysecret")

do_work()

```

✅ **Output:**
```
INFO: email=[REDACTED]
INFO: User signed in: email=[REDACTED], password=[REDACTED], api_key=[REDACTED], token=[REDACTED]
INFO: Payment info: card=[REDACTED], uuid=[REDACTED], aws=[REDACTED]
```

---

## 🧠 How It Works

`logguard` uses a **hybrid redaction model**:

1. **Keyword matching**  
   Searches for field names like `password`, `token`, `api_key`, `client_secret` from `sensitive_keys.txt`.  
   ```
   password=12345 → password=[REDACTED]
   ```

2. **Heuristic detection**  
   Even if a field name isn’t known, patterns like long random strings, emails, or UUIDs are automatically redacted.  
   ```
   token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 → token=[REDACTED]
   ```

This ensures no sensitive value leaks into log files — even when variable names differ.

---

## 🧰 Advanced Usage

### Custom Sensitive Keys
You can extend the default `sensitive_keys.txt` file with your own entries:
```
custom_secret
internal_token
```
Reload your package or re-import `logguard` to apply them.

---

### Direct Redaction Function
You can also manually call the sanitizer:

```python
from logguard import redact

text = "email=user@example.com, password=secret123"
print(redact(text))
# → email=[REDACTED], password=[REDACTED]
```

---

## 🧩 Example Patterns (v2)

| Type | Example | Redacted |
|------|----------|-----------|
| Email | `user@example.com` | `[REDACTED]` |
| Token | `abcd1234efgh5678ijkl9012` | `[REDACTED]` |
| UUID | `550e8400-e29b-41d4-a716-446655440000` | `[REDACTED]` |
| Credit Card | `4111-1111-1111-1111` | `[REDACTED]` |
| JWT | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9` | `[REDACTED]` |
| AWS Key | `AKIA1234567890ABCDEF` | `[REDACTED]` |

[//]: # (---)

[//]: # ()
[//]: # (## 🧪 Development & Packaging)

[//]: # ()
[//]: # (The package includes:)

[//]: # (- `pyproject.toml` — build configuration &#40;setuptools&#41;)

[//]: # (- `setup.cfg` — metadata)

[//]: # (- `sensitive_keys.txt` — large curated list of field names)

[//]: # (- Example usage script &#40;`example.py`&#41;)

[//]: # ()
[//]: # (To build locally:)

[//]: # (```bash)

[//]: # (python3 -m build)

[//]: # (```)

[//]: # ()
[//]: # (To upload &#40;for testing&#41;:)

[//]: # (```bash)

[//]: # (python3 -m twine upload --repository testpypi dist/*)

[//]: # (```)

---

## ⚠️ Notes

- Avoid excessive redaction in structured logs  
- Regex-based redaction may slightly impact performance on large-scale systems  
- Future versions will add:
  - JSON-aware redaction
  - Async logging support
  - Developer tagging (`@sensitive` decorator)

---

## 🧡 License
MIT License © 2025 — Developed for safe and responsible logging.
