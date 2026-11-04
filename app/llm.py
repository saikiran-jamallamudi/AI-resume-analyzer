"""Optional OpenAI-compatible recommendations; no-op when not configured."""

import os

import requests


def generate_llm_recommendations(analysis, resume_text, job_description):
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        return None

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    endpoint = f"{base_url}/chat/completions"

    system_prompt = (
        "You are a careful career-document coach. Compare a resume to a job "
        "description. Never invent experience, credentials, metrics, or skills. "
        "Return concise, specific recommendations grounded in the supplied text. "
        "Do not make hiring predictions."
    )
    user_prompt = (
        "Review the following analysis and source text. Return 4 to 6 practical "
        "recommendations in plain text. Identify evidence the candidate could "
        "clarify, but explicitly say not to claim skills they do not have.\n\n"
        f"Analysis: {analysis}\n\nResume:\n{resume_text[:12000]}\n\n"
        f"Job description:\n{job_description[:12000]}"
    )

    try:
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            return None
        return [
            line.strip().lstrip("-•0123456789. ").strip()
            for line in content.splitlines()
            if line.strip()
        ][:8]
    except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
        # A failed external API should not make the core analysis unavailable.
        return None
