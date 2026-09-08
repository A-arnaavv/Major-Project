import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

_client = None


def get_gemini_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please check your .env file."
            )

        _client = genai.Client(api_key=api_key)

    return _client


def generate_response(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the generated response.
    """

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )

    return response.text