# app/gemini_client.py
import os
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(prompt: str, context_text: str = None, model: str = "gemini-2.5-pro"):
    """
    Simple wrapper to call generate_content with context included in prompt.
    Returns plain text answer.
    """
    contents = []
    if context_text:
        # pass context as a separate part to keep it explicit
        contents.append(context_text)
    contents.append(prompt)

    resp = client.models.generate_content(
        model=model,
        contents=contents,
        # optionally configure response length, temperature, safety etc via config
        # config=types.GenerateContentConfig(max_output_tokens=800)
    )
    # The SDK returns a pydantic object; text field contains answer
    return resp.text