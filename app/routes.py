import json
import os

from flask import Blueprint, current_app, jsonify, render_template, request, send_file
from io import BytesIO

from .analyzer import analyze_resume
from .extractors import extract_resume_text
from .llm import generate_llm_recommendations

main = Blueprint("main", __name__)


@main.get("/")
def index():
    return render_template("index.html")


@main.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "llm_enabled": bool(os.getenv("LLM_API_KEY", "").strip()),
    })


def _get_analysis_inputs():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        return str(payload.get("resume_text", "")), str(payload.get("job_description", ""))

    resume_text = request.form.get("resume_text", "")
    job_description = request.form.get("job_description", "")
    uploaded = request.files.get("resume")
    if uploaded and uploaded.filename:
        file_bytes = uploaded.read()
        if not file_bytes:
            raise ValueError("The uploaded file is empty.")
        resume_text = extract_resume_text(uploaded.filename, file_bytes)
    return resume_text, job_description


@main.post("/api/analyze")
def analyze():
    try:
        resume_text, job_description = _get_analysis_inputs()
        result = analyze_resume(resume_text, job_description)
        llm_recommendations = generate_llm_recommendations(
            result, resume_text, job_description
        )
        if llm_recommendations:
            result["recommendations"] = llm_recommendations
            result["recommendation_source"] = "llm"
        else:
            result["recommendation_source"] = "local"
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        current_app.logger.exception("Unexpected analysis error")
        return jsonify({"error": "Analysis failed unexpectedly. Please try again."}), 500


@main.post("/api/report")
def report():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "match_score" not in payload:
        return jsonify({"error": "A valid analysis result is required."}), 400

    report_bytes = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    return send_file(
        BytesIO(report_bytes),
        mimetype="application/json",
        as_attachment=True,
        download_name="resume-analysis-report.json",
    )


@main.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "Upload too large. Maximum file size is 5 MB."}), 413
