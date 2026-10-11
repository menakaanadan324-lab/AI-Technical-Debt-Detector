from analyzer import analyze_code
from refactor import safe_format_code

def test_analyze_valid_code():
    result = analyze_code("def hello():\n    return 'hi'\n")
    assert result["syntax_error"] is None
    assert result["functions"] == 1
    assert "issues" in result

def test_syntax_error_is_reported():
    result = analyze_code("def broken(:\n  pass")
    assert result["syntax_error"] is not None

def test_safe_formatting():
    output, changes = safe_format_code("x = 1   ")
    assert output == "x = 1\n"
    assert changes

def test_empty_issues_summary():
    result = analyze_code("")
    assert result["summary"] == {"high": 0, "medium": 0, "low": 0}
