import logging
import sys
import uuid
from contextvars import ContextVar

from config import LOG_LEVEL

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="no-trace")


class TraceFormatter(logging.Formatter):
    def format(self, record):
        record.trace_id = trace_id_var.get("no-trace")
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = TraceFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    return logger


def generate_trace_id() -> str:
    return str(uuid.uuid4())[:8]
