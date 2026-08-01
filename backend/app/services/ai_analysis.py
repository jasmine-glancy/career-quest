import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.config import settings


class AIServiceError(Exception):
    """Raised when the LLM call fails or returns an unusable response."""


JOB_FIT_SYSTEM_PROMPT = (
    "You are a career coach comparing a candidate's resume against a job "
    "description. Respond ONLY with a JSON object matching this exact shape: "
    '{"match_score": <int 0-100>, "strengths": [<string>, ...], '
    '"gaps": [<string>, ...], "recommendations": [<string>, ...]}. '
    "Do not include any other keys or commentary."
)

RESUME_OPTIMIZE_SYSTEM_PROMPT = (
    "You are a resume editor tailoring a candidate's resume to a specific job. "
    "Respond ONLY with a JSON object matching this exact shape: "
    '{"summary": <string>, "suggested_edits": [{"section": <string>, '
    '"suggestion": <string>}, ...], "missing_keywords": [<string>, ...]}. '
    "Do not include any other keys or commentary."
)


def _client() -> OpenAI:
    if not settings.openai_api_key:
        raise AIServiceError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=settings.openai_api_key)


def _build_context(resume_snapshot: dict[str, Any], job_title: str, job_description: str | None) -> str:
    return (
        f"Resume (structured JSON):\n{json.dumps(resume_snapshot)}\n\n"
        f"Job title: {job_title}\n"
        f"Job description:\n{job_description or '(none provided)'}"
    )


def _chat_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    client = _client()
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except OpenAIError as exc:
        raise AIServiceError(f"OpenAI request failed: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise AIServiceError("OpenAI returned an empty response")

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIServiceError(f"OpenAI returned invalid JSON: {exc}") from exc


def generate_job_fit_analysis(
    resume_snapshot: dict[str, Any], job_title: str, job_description: str | None
) -> dict[str, Any]:
    result = _chat_json(JOB_FIT_SYSTEM_PROMPT, _build_context(resume_snapshot, job_title, job_description))

    required_keys = {"match_score", "strengths", "gaps", "recommendations"}
    missing = required_keys - result.keys()
    if missing:
        raise AIServiceError(f"OpenAI response missing required keys: {missing}")
    return result


def generate_resume_optimization(
    resume_snapshot: dict[str, Any], job_title: str, job_description: str | None
) -> dict[str, Any]:
    result = _chat_json(
        RESUME_OPTIMIZE_SYSTEM_PROMPT, _build_context(resume_snapshot, job_title, job_description)
    )

    required_keys = {"summary", "suggested_edits", "missing_keywords"}
    missing = required_keys - result.keys()
    if missing:
        raise AIServiceError(f"OpenAI response missing required keys: {missing}")
    return result
