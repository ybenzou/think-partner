import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def expand_with_gemini(prompt: str) -> list[str]:
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()
        print("🌟 Gemini raw response:", text)

        return [line.strip(" \n-•1234567890.").strip() for line in text.split("\n") if line.strip()]
    except Exception as e:
        print("❌ Gemini API error:", e)
        return []
