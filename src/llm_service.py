import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
use_mock = os.getenv("USE_MOCK_LLM", "true").lower() == "true"

client = OpenAI(api_key=api_key) if api_key else None


def _mock_type(user_input: str) -> str:
    text = user_input.lower()

    form_keywords = [
        "form", "application", "field", "question", "legal status",
        "proof", "residence", "current address", "document", "write", "fill"
    ]
    general_keywords = [
        "what", "how", "where", "when", "do i need", "can i", "should i", "meaning"
    ]

    if any(k in text for k in form_keywords):
        return "form_help"
    if any(k in text for k in general_keywords):
        return "simple_qa"
    return "simple_qa"


def get_mock_response(user_input: str) -> str:
    detected_type = _mock_type(user_input)

    if detected_type == "form_help":
        return f"""
Type: form_help

Simple explanation:
This looks like a form-related question. The app understands that you need help explaining an official field or written requirement.

What is expected:
The user likely needs a short and clear explanation of what the form is asking. If location matters, canton is enough.

Example answer:
I currently live in the canton of Zurich.

Safety note:
This tool gives general guidance only and does not replace official or legal advice. Do not share unnecessary personal details.
""".strip()

    return f"""
Type: simple_qa

Simple explanation:
This looks like a simple administrative question. The app understands that the user needs first-step guidance in plain language.

What is expected:
The user needs a short and supportive explanation. If location is relevant, mention canton only.

Example answer:
If the form asks where you live, it may be enough to mention your canton, for example: Canton of Bern.

Safety note:
This tool gives general guidance only and does not replace official or legal advice. Do not share unnecessary personal details.
""".strip()


def _call_openai(user_input: str) -> str:
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Make sure your .env file exists in the project root."
        )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for refugees in Switzerland. "
                    "First classify the user's message into exactly one of these types: "
                    "form_help, simple_qa, out_of_scope. "
                    "Then answer in simple English. "
                    "If it is form_help, explain the form question clearly and say what information is expected. "
                    "If it is simple_qa, give short first-step guidance. "
                    "If it is out_of_scope, say clearly that the request is outside the tool's purpose. "
                    "Do not give legal advice. "
                    "Do not ask for a full home address. "
                    "If location is relevant, mention canton only. "
                    "Encourage data minimization and avoid unnecessary personal details. "
                    "Return the answer in this exact format:\n"
                    "Type: ...\n"
                    "Simple explanation: ...\n"
                    "What is expected: ...\n"
                    "Example answer: ...\n"
                    "Safety note: ..."
                ),
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )
    return response.output_text


def process_user_input(user_input: str) -> str:
    if use_mock:
        return get_mock_response(user_input)

    try:
        return _call_openai(user_input)
    except Exception as e:
        return f"""
Type: error

Simple explanation:
The live AI service is currently unavailable.

What is expected:
Please try again later or use mock mode for development.

Example answer:
Temporary fallback activated.

Safety note:
Error details: {str(e)}
""".strip()