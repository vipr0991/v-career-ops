#!/usr/bin/env python3
"""
Career-Ops Test & Launch Server
Minimal test to verify backend is working
"""

import sys
import os
import time

print("\n" + "="*60)
print("  CAREER-OPS TEST SERVER")
print("="*60 + "\n")

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and start the API
print("[1/3] Loading API...")
try:
    from career_ops_api import app
    print("  ✓ API loaded successfully\n")
except Exception as e:
    print(f"  ✗ Failed to load API: {e}\n")
    sys.exit(1)

# Test import all dependencies
print("[2/3] Checking dependencies...")
try:
    import fastapi
    import uvicorn
    import pydantic
    import httpx
    print("  ✓ All dependencies OK\n")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}\n")
    print("  Fix: pip install -r requirements.txt\n")
    sys.exit(1)

# Start server
print("[3/3] Starting API server on http://0.0.0.0:5000")
print("  This window must stay open!\n")
print("  Press CTRL+C to stop\n")
print("-"*60 + "\n")

try:
    import uvicorn
    # Run with explicit config
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        access_log=True
    )
except KeyboardInterrupt:
    print("\n\nShutdown requested")
except Exception as e:
    print(f"\n✗ Server error: {e}")
    sys.exit(1)
