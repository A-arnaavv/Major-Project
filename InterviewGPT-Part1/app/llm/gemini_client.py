import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()


# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )


# Create Gemini client
client = genai.Client(api_key=api_key)


def generate_response(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the generated response.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text