import json
import logging
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.config import settings
from app.schemas.ai_analysis import JobFitAnalysisResult, OptimizeResumeResponse

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when the LLM call fails or returns an unusable response."""


GENERIC_FAILURE_MESSAGE = "AI service is temporarily unavailable. Please try again."

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
        raise AIServiceError(GENERIC_FAILURE_MESSAGE)
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
        # The raw exception can echo back request details (e.g. a masked fragment of
        # the API key on an auth failure) — log it server-side only, never in the
        # client-facing error.
        logger.error("OpenAI request failed: %s", exc)
        raise AIServiceError(GENERIC_FAILURE_MESSAGE) from exc

    if not response.choices:
        logger.error("OpenAI returned no choices")
        raise AIServiceError(GENERIC_FAILURE_MESSAGE)

    content = response.choices[0].message.content
    if not content:
        logger.error("OpenAI returned an empty response")
        raise AIServiceError(GENERIC_FAILURE_MESSAGE)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("OpenAI returned invalid JSON: %s", exc)
        raise AIServiceError(GENERIC_FAILURE_MESSAGE) from exc


def generate_job_fit_analysis(
    resume_snapshot: dict[str, Any], job_title: str, job_description: str | None
) -> JobFitAnalysisResult:
    raw = _chat_json(JOB_FIT_SYSTEM_PROMPT, _build_context(resume_snapshot, job_title, job_description))
    try:
        return JobFitAnalysisResult.model_validate(raw)
    except ValidationError as exc:
        logger.error("OpenAI response failed validation: %s", exc)
        raise AIServiceError(GENERIC_FAILURE_MESSAGE) from exc


def generate_resume_optimization(
    resume_snapshot: dict[str, Any], job_title: str, job_description: str | None
) -> OptimizeResumeResponse:
    raw = _chat_json(RESUME_OPTIMIZE_SYSTEM_PROMPT, _build_context(resume_snapshot, job_title, job_description))
    try:
        return OptimizeResumeResponse.model_validate(raw)
    except ValidationError as exc:
        logger.error("OpenAI response failed validation: %s", exc)
        raise AIServiceError(GENERIC_FAILURE_MESSAGE) from exc
