import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_question(user_input: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": "You help refugees in Switzerland understand official forms in simple language. Do not provide legal advice."
            },
            {
                "role": "user",
                "content": f"Explain this question simply, say what is expected, and give an example answer if possible: {user_input}"
            }
        ]
    )
    return response.output_text
