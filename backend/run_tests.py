import pytest
import sys
from io import StringIO

if __name__ == "__main__":
    # Capture stdout/stderr
    capture = StringIO()
    sys.stdout = capture
    sys.stderr = capture
    
    try:
        ret = pytest.main(["-v", "test_dedup_freshness.py"])
    except Exception as e:
        print(f"Exception: {e}")
        ret = 1
        
    # Write to file
    with open("test_debug.txt", "w", encoding="utf-8") as f:
        f.write(capture.getvalue())
        
    sys.exit(ret)
