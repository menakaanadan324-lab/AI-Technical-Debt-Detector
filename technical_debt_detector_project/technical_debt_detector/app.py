from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route("/debug-template")
def debug_template():
    template_path = os.path.abspath(
        os.path.join(app.root_path, app.template_folder, "index.html")
    )

    return jsonify({
        "app_file": os.path.abspath(_file_),
        "template_folder": app.template_folder,
        "template_path": template_path,
        "template_exists": os.path.isfile(template_path)
    })
@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Please send a valid JSON object."}), 400

    code = data.get("code")

    if not isinstance(code, str) or not code.strip():
        return jsonify({
            "error": "Please enter some Python code to analyze."
        }), 400

    if len(code) > MAX_CODE_LENGTH:
        return jsonify({
            "error": "Code is too large. Maximum size is 100,000 characters."
        }), 400

    try:
        findings = analyze_code(code)

        weights = {"high": 15, "medium": 8, "low": 3}
        score = max(
            0,
            100 - sum(weights[item["severity"]] for item in findings)
        )

        return jsonify({
            "score": score,
            "total": len(findings),
            "findings": findings,
            "message": (
                "Analysis complete. This is a heuristic estimate, "
                "not a definitive measure of technical debt."
            )
        })

    except Exception:
        app.logger.exception("Code analysis failed")
        return jsonify({
            "error": "Analysis failed on the server. Check the Flask terminal."
        }), 500
if __name__ == '__main__':
    app.run(debug=True)