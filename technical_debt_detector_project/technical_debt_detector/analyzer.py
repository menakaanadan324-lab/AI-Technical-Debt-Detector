import ast
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def analyze_code(code, filename="pasted_code.py"):
    """Analyze Python source using AST and Radon metrics; no code is executed."""
    lines = code.splitlines()
    result = {
        "filename": filename,
        "lines": len(lines),
        "non_empty_lines": sum(1 for line in lines if line.strip()),
        "functions": 0,
        "classes": 0,
        "total_complexity": 0,
        "maintainability_index": None,
        "issues": [],
        "summary": {"high": 0, "medium": 0, "low": 0},
        "syntax_error": None,
        "score": 100
    }
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        result["syntax_error"] = {
            "message": exc.msg,
            "line": exc.lineno,
            "offset": exc.offset
        }
        result["score"] = 0
        return result

    functions = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    result["functions"] = len(functions)
    result["classes"] = len(classes)

    try:
        blocks = cc_visit(code)
        result["total_complexity"] = sum(b.complexity for b in blocks)
        for block in blocks:
            if block.complexity >= 11:
                result["issues"].append(issue(
                    "High cyclomatic complexity", "High", block.lineno,
                    f"'{block.name}' has complexity {block.complexity}. Consider simplifying branches or extracting smaller functions.",
                    "Simplify conditional logic, use guard clauses, or split the function into smaller, well-named functions.",
                    12
                ))
            elif block.complexity >= 6:
                result["issues"].append(issue(
                    "Moderate cyclomatic complexity", "Medium", block.lineno,
                    f"'{block.name}' has complexity {block.complexity}.",
                    "Review nested conditions and consider extracting cohesive helper functions.",
                    6
                ))
    except Exception:
        pass

    try:
        result["maintainability_index"] = round(mi_visit(code, multi=True), 1)
    except Exception:
        result["maintainability_index"] = None

    for node in functions:
        end = getattr(node, "end_lineno", node.lineno)
        length = end - node.lineno + 1
        if length > 30:
            result["issues"].append(issue(
                "Long function", "Medium", node.lineno,
                f"Function '{node.name}' spans about {length} lines.",
                "Consider extracting cohesive blocks into helper functions while preserving behavior.",
                6
            ))
        if len(node.args.args) > 6:
            result["issues"].append(issue(
                "Too many parameters", "Low", node.lineno,
                f"Function '{node.name}' has {len(node.args.args)} parameters.",
                "Consider grouping related parameters into a data class or configuration object when appropriate.",
                3
            ))
        if not ast.get_docstring(node):
            result["issues"].append(issue(
                "Missing function docstring", "Low", node.lineno,
                f"Function '{node.name}' has no docstring.",
                "Add a concise docstring describing purpose, arguments, and return value.",
                2
            ))

    for node in classes:
        if not ast.get_docstring(node):
            result["issues"].append(issue(
                "Missing class docstring", "Low", node.lineno,
                f"Class '{node.name}' has no docstring.",
                "Document the class responsibility and important usage details.",
                2
            ))

    # Basic duplicate-line heuristic (ignores blank lines and comments).
    seen = {}
    for idx, line in enumerate(lines, start=1):
        normalized = line.strip()
        if len(normalized) >= 20 and not normalized.startswith("#"):
            if normalized in seen:
                result["issues"].append(issue(
                    "Repeated source line", "Low", idx,
                    f"A similar long line also appears on line {seen[normalized]}. This heuristic may include legitimate repetition.",
                    "Review whether the repeated logic should be moved into a shared helper. Confirm the code is truly duplicated before changing it.",
                    2
                ))
            else:
                seen[normalized] = idx

    result["issues"].sort(key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}[x["severity"]], x["line"] or 0))
    for item in result["issues"]:
        result["summary"][item["severity"].lower()] += 1
    penalty = sum(i["weight"] for i in result["issues"])
    result["score"] = max(0, min(100, 100 - penalty))
    result["score_note"] = "Heuristic indicator (not a validated industry score or ML prediction)."
    result["analysis_note"] = "Static analysis only: source code was parsed, not executed. Findings are suggestions and may include false positives."
    return result

def issue(title, severity, line, description, recommendation, weight):
    return {
        "title": title,
        "severity": severity,
        "line": line,
        "description": description,
        "recommendation": recommendation,
        "weight": weight
    }
