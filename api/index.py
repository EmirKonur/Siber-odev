"""
Vercel Serverless Function Entry Point
This file serves as the entry point for Vercel serverless deployment.
"""
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects the app to be named 'app' or handler
# The Flask app will handle all routes
