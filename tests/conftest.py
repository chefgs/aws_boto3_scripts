"""Shared pytest configuration."""
import os
import sys

# Ensure repo root is on the path so utils/ and services/ can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
