# DebtLens — AI-Powered Autonomous Technical Debt Detection and Refactoring System

A local academic prototype for Python source-code analysis. It uses Python AST and Radon metrics, heuristic rules, recommendations, and a conservative formatting preview.

## Features
- Paste source code or upload a `.py` file
- Parse Python syntax without executing submitted source
- Show line counts, function/class counts, cyclomatic complexity, and Radon maintainability index
- Flag selected complexity, long-function, parameter-count, docstring, and repeated-line heuristics
- Filter findings by severity
- Preview conservative formatting cleanup
- Export a JSON report
- Run basic unit tests

## Important scope notes
- This version is a working rule-based/static-analysis prototype, not a trained AI/ML model.
- The “quality indicator” is a simple heuristic score and is not a validated industry metric.
- Repeated-line detection is a basic heuristic and can produce false positives.
- “Safe formatting cleanup” only trims trailing whitespace and ensures a final newline. It does not rewrite program logic.
- Static analysis cannot guarantee behavior preservation. Review findings and test code before using changes.
- Source code is not executed by the analyzer.

## Requirements
- Python 3.10 or newer recommended
- VS Code (or another editor)
- Internet only for installing dependencies; the app itself runs locally.

## Setup — Windows
Open this folder in VS Code, then use Terminal > New Terminal:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\\Scripts\\activate.bat
```

Open http://127.0.0.1:5000 in your browser.

## Setup — macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000.

## Tests
With the virtual environment activated:
```bash
pytest -q
```

## Suggested project demonstration
1. Open the local dashboard.
2. Paste a Python function with many branches or a long body.
3. Select Analyze code.
4. Show issue severity, line numbers, recommendations, and code metrics.
5. Export the JSON report.
6. Preview formatting cleanup and explain that it is deliberately limited.
7. Run tests and discuss the limitations of rule-based detection.

## Suggested next development tasks
1. Build a labeled dataset of examples and refactor types.
2. Train/evaluate a classifier using scikit-learn and compare it with the rule baseline.
3. Add token-aware or AST-based duplicate-code detection.
4. Implement narrowly scoped AST transformations with tests and diff preview.
5. Add test execution in an isolated subprocess/container before accepting refactored code.
6. Add report history only if persistence is needed.
