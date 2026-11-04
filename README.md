# AI Resume Analyzer

A Flask web application that compares a resume with a job description, identifies matched and missing skills, estimates keyword coverage, and generates actionable improvement recommendations.

## Features

- Upload PDF or DOCX resumes, or paste resume text.
- Paste a job description and analyze it in one click.
- Extract skills from both documents using a curated, extensible skill catalog.
- Show matched skills, missing skills, keyword coverage, and a transparent match score.
- Generate practical recommendations using a deterministic fallback or an optional OpenAI-compatible chat-completions API.
- Export an analysis report as JSON.
- Input validation, file-size limits, safe temporary-file handling, and useful error messages.
- Includes unit tests and a sample job description.

> The match score is a heuristic based on extracted skills and keyword overlap. It is not an ATS score, hiring probability, or guarantee of shortlisting.

## Tech stack

Python 3.10+, Flask, PyMuPDF, python-docx, HTML, CSS, and JavaScript.

## Quick start

### 1. Create and activate a virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and set a secret key. LLM configuration is optional.

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

### 4. Run

```bash
python run.py
```

Open http://127.0.0.1:5000.

## Optional LLM recommendations

Set these variables in `.env` to enable LLM-generated recommendations:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

The application uses the OpenAI-compatible `/chat/completions` interface. Keep API keys on the server. The app never sends a resume to an LLM unless an API key is configured and the user submits an analysis. Without configuration, a local recommendation engine is used.

## API

### POST /api/analyze

Accepts JSON with `resume_text` and `job_description`, or multipart form data with a `resume` file and `job_description`.

JSON example:

```json
{
  "resume_text": "Python developer with Flask, SQL, Git and REST API experience.",
  "job_description": "We need a Python engineer with Flask, PostgreSQL, REST APIs and Docker."
}
```

Response includes:
- `match_score`: heuristic score from 0 to 100
- `matched_skills`
- `missing_skills`
- `resume_skills`
- `job_skills`
- `keyword_coverage`
- `recommendations`
- `summary`

### GET /api/health

Returns application health and whether optional LLM configuration is enabled.

### POST /api/report

Accepts an analysis JSON object and returns a downloadable JSON report.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```
app/
  __init__.py
  analyzer.py
  extractors.py
  llm.py
  routes.py
  templates/index.html
  static/css/styles.css
  static/js/app.js
tests/
  test_analyzer.py
  test_routes.py
sample_data/
  sample_job_description.txt
.env.example
.gitignore
requirements.txt
run.py
```

## Privacy and security notes

- Uploaded files are parsed in memory and are not saved permanently.
- The app limits uploads to 5 MB and accepts PDF and DOCX only.
- Never commit `.env` or API credentials.
- For production, use HTTPS, a production WSGI server, rate limiting, and a managed secret store.
- Do not use automated scores as a substitute for human review.

## Roadmap

- Add more skill aliases and language-specific extraction.
- Add persistent user accounts and saved analysis history.
- Add semantic embeddings and explainable section-level scoring.
- Add deployment configuration for a production hosting provider.
