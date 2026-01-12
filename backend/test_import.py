import sys
sys.path.insert(0, '.')

try:
    from app.routes import router
    print(f"✓ Router imported successfully: {router}")
    print(f"✓ Router type: {type(router)}")
    print(f"✓ Router routes: {router.routes}")
    print(f"✓ Number of routes: {len(router.routes)}")
    for route in router.routes:
        print(f"  - {route.path} ({route.methods if hasattr(route, 'methods') else 'N/A'})")
except Exception as e:
    print(f"✗ Error importing router: {e}")
    import traceback
    traceback.print_exc()
