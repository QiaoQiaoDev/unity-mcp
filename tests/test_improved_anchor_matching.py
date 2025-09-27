"""
Test the improved anchor matching logic.
"""

import sys
import pathlib
import importlib.util
import types

# add server src to path and load modules
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "UnityMcpBridge" / "UnityMcpServer~" / "src"
sys.path.insert(0, str(SRC))

# stub mcp.server.fastmcp
mcp_pkg = types.ModuleType("mcp")
server_pkg = types.ModuleType("mcp.server")
fastmcp_pkg = types.ModuleType("mcp.server.fastmcp")

class _Dummy:
    pass

fastmcp_pkg.FastMCP = _Dummy
fastmcp_pkg.Context = _Dummy
server_pkg.fastmcp = fastmcp_pkg
mcp_pkg.server = server_pkg
sys.modules.setdefault("mcp", mcp_pkg)
sys.modules.setdefault("mcp.server", server_pkg)
sys.modules.setdefault("mcp.server.fastmcp", fastmcp_pkg)

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

manage_script_edits_module = load_module(SRC / "tools" / "manage_script_edits.py", "manage_script_edits_module")

def test_improved_anchor_matching():
    """Test that our improved anchor matching finds the right closing brace."""
    
    test_code = '''using UnityEngine;

public class TestClass : MonoBehaviour  
{
    void Start()
    {
        Debug.Log("test");
    }
    
    void Update()
    {
        // Update logic
    }
}'''
    
    import re
    
    # Test the problematic anchor pattern
    anchor_pattern = r"\s*}\s*$"
    flags = re.MULTILINE
    
    # Test our improved function
    best_match = manage_script_edits_module._find_best_anchor_match(
        anchor_pattern, test_code, flags, prefer_last=True
    )
    
    assert best_match is not None, "anchor pattern not found"
    match_pos = best_match.start()
    line_num = test_code[:match_pos].count('\n') + 1
    total_lines = test_code.count('\n') + 1
    assert line_num >= total_lines - 2, f"expected match near end (>= {total_lines-2}), got line {line_num}"

def test_old_vs_new_matching():
    """Compare old vs new matching behavior."""
    
    test_code = '''using UnityEngine;

public class TestClass : MonoBehaviour  
{
    void Start()
    {
        Debug.Log("test");
    }
    
    void Update()
    {
        if (condition)
        {
            DoSomething();
        }
    }
    
    void LateUpdate()
    {
        // More logic
    }
}'''
    
    import re
    
    anchor_pattern = r"\s*}\s*$"
    flags = re.MULTILINE
    
    # Old behavior (first match)
    old_match = re.search(anchor_pattern, test_code, flags)
    old_line = test_code[:old_match.start()].count('\n') + 1 if old_match else None
    
    # New behavior (improved matching)
    new_match = manage_script_edits_module._find_best_anchor_match(
        anchor_pattern, test_code, flags, prefer_last=True
    )
    new_line = test_code[:new_match.start()].count('\n') + 1 if new_match else None
    
    assert old_line is not None and new_line is not None, "failed to locate anchors"
    assert new_line > old_line, f"improved matcher should choose a later line (old={old_line}, new={new_line})"
    total_lines = test_code.count('\n') + 1
    assert new_line >= total_lines - 2, f"expected class-end match near end (>= {total_lines-2}), got {new_line}"

def test_apply_edits_with_improved_matching():
    """Test that _apply_edits_locally uses improved matching."""
    
    original_code = '''using UnityEngine;

public class TestClass : MonoBehaviour
{
    public string message = "Hello World";
    
    void Start()
    {
        Debug.Log(message);
    }
}'''
    
    # Test anchor_insert with the problematic pattern
    edits = [{
        "op": "anchor_insert",
        "anchor": r"\s*}\s*$",  # This should now find the class end
        "position": "before",
        "text": "\n    public void NewMethod() { Debug.Log(\"Added at class end\"); }\n"
    }]
    
    result = manage_script_edits_module._apply_edits_locally(original_code, edits)
    lines = result.split('\n')
    try:
        idx = next(i for i, line in enumerate(lines) if "NewMethod" in line)
    except StopIteration:
        assert False, "NewMethod not found in result"
    total_lines = len(lines)
    assert idx >= total_lines - 5, f"method inserted too early (idx={idx}, total_lines={total_lines})"

def _run_test(label, func):
    """Execute a test function and return True on success for script usage."""

    try:
        func()
    except AssertionError as exc:
        print(f"❌ {label} failed: {exc}")
        return False
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"❌ {label} errored: {exc}")
        return False
    else:
        print(f"✅ {label} passed")
        return True


if __name__ == "__main__":
    print("Testing improved anchor matching...")
    print("=" * 60)

    success1 = _run_test("Improved anchor matching", test_improved_anchor_matching)

    print("\n" + "=" * 60)
    print("Comparing old vs new behavior...")
    success2 = _run_test("Old vs new matching", test_old_vs_new_matching)

    print("\n" + "=" * 60)
    print("Testing _apply_edits_locally with improved matching...")
    success3 = _run_test(
        "_apply_edits_locally with improved matching",
        test_apply_edits_with_improved_matching,
    )

    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 ALL TESTS PASSED! Improved anchor matching is working!")
    else:
        print("💥 Some tests failed. Need more work on anchor matching.")
