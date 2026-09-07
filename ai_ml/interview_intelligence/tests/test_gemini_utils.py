from ai_ml.interview_intelligence.gemini_utils import (
    call_gemini_with_retry,
)


class FakeAPIError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f"Fake API error {code}")


def test_success_without_retry(monkeypatch):
    calls = {"count": 0}

    def operation():
        calls["count"] += 1
        return "success"

    result = call_gemini_with_retry(
        operation=operation,
        max_attempts=2,
        base_delay=0,
    )

    assert result == "success"
    assert calls["count"] == 1


def test_connection_error_retries():
    calls = {"count": 0}

    def operation():
        calls["count"] += 1

        if calls["count"] == 1:
            raise ConnectionError("temporary failure")

        return "success"

    result = call_gemini_with_retry(
        operation=operation,
        max_attempts=2,
        base_delay=0,
    )

    assert result == "success"
    assert calls["count"] == 2


def test_connection_error_fails_after_max_attempts():
    def operation():
        raise ConnectionError("still unavailable")

    try:
        call_gemini_with_retry(
            operation=operation,
            max_attempts=2,
            base_delay=0,
        )

        assert False, "Expected RuntimeError"

    except RuntimeError as exc:
        assert "failed after 2 attempts" in str(exc)