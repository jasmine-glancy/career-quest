import pytest
from openai import OpenAIError

import app.services.ai_analysis as ai_service
from app.schemas.ai_analysis import JobFitAnalysisResult, OptimizeResumeResponse
from app.services.ai_analysis import (
    GENERIC_FAILURE_MESSAGE,
    AIServiceError,
    generate_job_fit_analysis,
    generate_resume_optimization,
)

VALID_JOB_FIT_JSON = (
    '{"match_score": 82, "strengths": ["Strong SQL"], "gaps": ["No AWS"], '
    '"recommendations": ["Add AWS"], "matched_skills": ["SQL"], "missing_skills": ["AWS"]}'
)
VALID_OPTIMIZE_JSON = (
    '{"summary": "Solid fit.", "suggested_edits": '
    '[{"section": "Experience", "suggestion": "Add metrics."}], "missing_keywords": ["dbt"]}'
)


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content=None, choices=None):
        self.choices = choices if choices is not None else [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self, response=None, exception=None):
        self._response = response
        self._exception = exception

    def create(self, **kwargs):
        if self._exception is not None:
            raise self._exception
        return self._response


class _FakeChat:
    def __init__(self, completions):
        self.completions = completions


class _FakeClient:
    def __init__(self, response=None, exception=None):
        self.chat = _FakeChat(_FakeCompletions(response=response, exception=exception))


def _patch_client(monkeypatch, response=None, exception=None):
    monkeypatch.setattr(ai_service, "_client", lambda: _FakeClient(response=response, exception=exception))


# --- error masking ---


def test_openai_error_is_masked_behind_generic_message(monkeypatch):
    _patch_client(monkeypatch, exception=OpenAIError("Incorrect API key provided: sk-fake123secret"))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE
    assert "sk-fake123secret" not in str(exc_info.value)


# --- choices/content guards ---


def test_empty_choices_raises_generic_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(choices=[]))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_empty_content_raises_generic_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content=""))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_invalid_json_raises_generic_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content="not json"))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


# --- generate_job_fit_analysis: schema validation ---


def test_generate_job_fit_analysis_returns_validated_result(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content=VALID_JOB_FIT_JSON))

    result = generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert isinstance(result, JobFitAnalysisResult)
    assert result.match_score == 82
    assert result.strengths == ["Strong SQL"]
    assert result.matched_skills == ["SQL"]
    assert result.missing_skills == ["AWS"]


def test_generate_job_fit_analysis_missing_key_raises_generic_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content='{"match_score": 82, "strengths": []}'))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_generate_job_fit_analysis_missing_skill_tags_raises_generic_error(monkeypatch):
    # Older-shape response with the prose fields but no matched_skills/missing_skills
    bad_json = (
        '{"match_score": 82, "strengths": ["Strong SQL"], "gaps": ["No AWS"], '
        '"recommendations": ["Add AWS"]}'
    )
    _patch_client(monkeypatch, response=_FakeResponse(content=bad_json))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_generate_job_fit_analysis_wrong_type_raises_generic_error(monkeypatch):
    # match_score as a non-numeric string can't coerce to int
    bad_json = (
        '{"match_score": "not-a-number", "strengths": [], "gaps": [], "recommendations": [], '
        '"matched_skills": [], "missing_skills": []}'
    )
    _patch_client(monkeypatch, response=_FakeResponse(content=bad_json))

    with pytest.raises(AIServiceError) as exc_info:
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_generate_job_fit_analysis_non_list_strengths_raises_generic_error(monkeypatch):
    bad_json = (
        '{"match_score": 80, "strengths": "not a list", "gaps": [], "recommendations": [], '
        '"matched_skills": [], "missing_skills": []}'
    )
    _patch_client(monkeypatch, response=_FakeResponse(content=bad_json))

    with pytest.raises(AIServiceError):
        generate_job_fit_analysis({"summary": "..."}, "Engineer", "Do things")


# --- generate_resume_optimization: schema validation ---


def test_generate_resume_optimization_returns_validated_result(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content=VALID_OPTIMIZE_JSON))

    result = generate_resume_optimization({"summary": "..."}, "Engineer", "Do things")

    assert isinstance(result, OptimizeResumeResponse)
    assert result.summary == "Solid fit."
    assert result.suggested_edits[0].section == "Experience"
    assert result.missing_keywords == ["dbt"]


def test_generate_resume_optimization_missing_key_raises_generic_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeResponse(content='{"summary": "..."}'))

    with pytest.raises(AIServiceError) as exc_info:
        generate_resume_optimization({"summary": "..."}, "Engineer", "Do things")

    assert str(exc_info.value) == GENERIC_FAILURE_MESSAGE


def test_generate_resume_optimization_malformed_edits_raises_generic_error(monkeypatch):
    bad_json = '{"summary": "ok", "suggested_edits": ["not an object"], "missing_keywords": []}'
    _patch_client(monkeypatch, response=_FakeResponse(content=bad_json))

    with pytest.raises(AIServiceError):
        generate_resume_optimization({"summary": "..."}, "Engineer", "Do things")
