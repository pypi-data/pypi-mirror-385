
import logging
from .redactor import redact

class RedactingFormatter(logging.Formatter):
    """
    A logging formatter that redacts sensitive data in record.msg and record.args
    """
    def format(self, record):
        try:
            if isinstance(record.msg, str):
                record.msg = redact(record.msg)
            # if args present and are a tuple, convert to redacted string representation
            if getattr(record, "args", None):
                try:
                    record.args = tuple(redact(str(a)) for a in record.args)
                except Exception:
                    record.args = ()
        except Exception:
            # never raise from logging
            pass
        return super().format(record)
