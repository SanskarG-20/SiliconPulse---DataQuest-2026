#!/usr/bin/env python
"""Direct test of FastAPI app to verify routes are registered"""

import sys
sys.path.insert(0, '.')

from app.main import app

print("FASTAPI APP ROUTE INSPECTION")
print("=" * 60)

print(f"\nApp object: {app}")
print(f"App title: {app.title}")

print(f"\nAll registered routes:")
print("-" * 60)
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(route.methods) if route.methods else 'N/A'
        print(f"  {methods:10} {route.path}")
    elif hasattr(route, 'path'):
        print(f"  {'MOUNT':10} {route.path}")

print("\n" + "=" * 60)
print("EXPECTED ROUTES:")
print("-" * 60)
expected = [
    "GET        /",
    "GET        /health",
    "POST       /api/inject",
    "POST       /api/query",
    "GET        /api/signals",
    "GET        /api/radar"
]
for exp in expected:
    print(f"  {exp}")

print("\n" + "=" * 60)
