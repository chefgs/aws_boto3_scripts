"""Shared argument-parsing helpers."""
import argparse


def base_parser(description=""):
    """Return an ArgumentParser pre-loaded with common AWS flags."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--profile", default=None, help="AWS profile name")
    parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making changes",
    )
    return parser
