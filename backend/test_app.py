"""
Test script to verify FastAPI app loads correctly
"""

from app.main import app

print("FastAPI app loaded successfully!")
print(f"App name: {app.title}")
print(f"Version: {app.version}\n")

# List all routes
routes = [route for route in app.routes if hasattr(route, 'path')]
auth_routes = [r for r in routes if '/auth' in r.path]

print(f"Total auth endpoints: {len(auth_routes)}\n")
print("Auth endpoints:")
for route in auth_routes:
    methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
    print(f"  [{methods:12}] {route.path}")

print("\nAll endpoints:")
for route in routes:
    methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
    print(f"  [{methods:12}] {route.path}")
