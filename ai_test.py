import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("API key nahi mili. .env file check karo.")
    raise SystemExit(1)

client = OpenAI(api_key=api_key)

try:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input="Reply in Hinglish: Namaste Jarvis, apna introduction do."
    )

    print("\nJARVIS AI:")
    print(response.output_text)

except Exception as error:
    print("API error:", error)