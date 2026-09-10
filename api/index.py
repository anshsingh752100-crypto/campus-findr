"""Vercel serverless entry point."""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("VERCEL", "1")

from app import app
