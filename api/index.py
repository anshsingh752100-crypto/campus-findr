"""
api/index.py — Vercel serverless entry point for Campus Findr.
"""

import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)

# Set Vercel env if not already set
os.environ.setdefault("VERCEL", "1")

from app import app

# Vercel handler — this is what @vercel/python looks for
def handler(request):
    """WSGI handler for Vercel."""
    return app(request.environ, request.start_response)
