"""Logging configuration helpers."""
import logging
import sys


def setup_logging(level=logging.INFO):
    """Configure root logger to output to stdout with a structured format."""
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    return logging.getLogger()
