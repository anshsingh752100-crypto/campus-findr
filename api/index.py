"""
api/index.py — Vercel serverless function entry point.

Imports the Flask app from the parent directory and exposes it
as a WSGI handler for Vercel's @vercel/python runtime.
"""

import sys
import os

# Add the project root to Python path so we can import app, models, database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app

# Vercel's @vercel/python runtime looks for the `app` variable
