import random
import time
from typing import Callable, TypeVar

from google.genai import errors


T = TypeVar("T")


TRANSIENT_STATUS_CODES = {
    408,  # Request timeout
    429,  # Rate limit / quota
    500,
    502,
    503,
    504,
}


def _get_status_code(error: Exception) -> int | None:
    """
    Extract an HTTP status code from different Gemini SDK
    exception formats.
    """

    for attribute in (
        "code",
        "status_code",
        "status",
    ):
        value = getattr(error, attribute, None)

        if isinstance(value, int):
            return value

    return None


def call_gemini_with_retry(
    operation: Callable[[], T],
    operation_name: str = "Gemini request",
    max_attempts: int = 2,
    base_delay: float = 1.0,
) -> T:
    """
    Execute a Gemini operation with lightweight application-level
    retry handling.

    The Google Gen AI SDK already performs some automatic retries,
    so this wrapper intentionally keeps its own retry count small.
    """

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):

        try:
            return operation()

        except errors.APIError as exc:
            last_error = exc

            status_code = _get_status_code(exc)

            # Do not retry permanent client errors such as
            # invalid API keys, invalid requests, etc.
            if status_code not in TRANSIENT_STATUS_CODES:
                raise RuntimeError(
                    f"{operation_name} failed "
                    f"with Gemini API error "
                    f"{status_code or 'unknown'}: {exc}"
                ) from exc

            if attempt == max_attempts:
                break

            # Exponential backoff + small random jitter
            delay = (
                base_delay * (2 ** (attempt - 1))
                + random.uniform(0, 0.5)
            )

            print(
                f"[Gemini] {operation_name} temporarily failed "
                f"(status {status_code}). "
                f"Retrying..."
            )

            time.sleep(delay)

        except (TimeoutError, ConnectionError) as exc:
            last_error = exc

            if attempt == max_attempts:
                break

            delay = (
                base_delay * (2 ** (attempt - 1))
                + random.uniform(0, 0.5)
            )

            print(
                f"[Gemini] {operation_name} encountered a "
                f"connection problem. Retrying..."
            )

            time.sleep(delay)

        except Exception as exc:
            # Unexpected errors should not silently retry.
            raise RuntimeError(
                f"{operation_name} failed unexpectedly: {exc}"
            ) from exc

    raise RuntimeError(
        f"{operation_name} failed after "
        f"{max_attempts} attempts: {last_error}"
    ) from last_error