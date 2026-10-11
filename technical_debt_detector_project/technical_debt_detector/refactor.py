def safe_format_code(code):
    """
    Conservative formatting cleanup only. This is not semantic refactoring.
    It strips trailing whitespace and ensures one final newline.
    """
    original = code
    cleaned_lines = [line.rstrip() for line in code.splitlines()]
    updated = "\n".join(cleaned_lines).rstrip() + "\n"
    changes = []
    if updated != original:
        changes.append("Removed trailing whitespace and normalized the final newline.")
    else:
        changes.append("No safe formatting changes were needed.")
    return updated, changes
