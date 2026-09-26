import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Determine path to APIs/groq.env
CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / "APIs" / "groq.env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# Get Groq API key from environment
api_key = os.getenv("groq_api_key") or os.getenv("GROQ_API_KEY")

DEFAULT_MODEL = "openai/gpt-oss-20b"

# Initialize Groq client
client = Groq(api_key=api_key) if api_key else None


def generate_mcqs(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send prompt to Groq API with JSON response format and return the response content string.
    """
    if not api_key or not client:
        raise ValueError(
            "Groq API key is missing. Please set 'groq_api_key' in APIs/groq.env or the GROQ_API_KEY environment variable."
        )

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )
    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    print("Testing Groq API connection...")
    try:
        test_response = generate_mcqs("What is 4+1? Return JSON with key 'answer'.")
        print("Response received successfully:")
        print(test_response)
    except Exception as e:
        print(f"Error testing Groq API: {e}")
