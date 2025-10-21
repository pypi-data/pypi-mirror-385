
import logging
from functools import wraps
from .redactor import redact

def _patch_logging_once():
    # patch common logging functions to redact messages; idempotent in effect
    # We use simple patching - for production you'd consider thread-safety and preserving all attributes
    for name in ("debug","info","warning","error","critical","exception","log"):
        orig = getattr(logging, name)
        def make_safe(orig_func):
            def safe(msg, *args, **kwargs):
                try:
                    if isinstance(msg, str):
                        msg = redact(msg)
                except Exception:
                    pass
                return orig_func(msg, *args, **kwargs)
            return safe
        safe_fn = make_safe(orig)
        setattr(logging, name, safe_fn)

_patched = False
def filter(func=None):
    """
    Decorator that ensures logging.* functions are patched to redact messages when the decorated function runs.
    Use as:

    @filter
    def f(...):
        logging.info("user password=secret")
    """
    global _patched
    if func is None:
        return lambda f: filter(f)
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _patched
        if not _patched:
            _patch_logging_once()
            _patched = True
        return func(*args, **kwargs)
    return wrapper
