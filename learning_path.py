import os
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def get_learning_recommendations(topic: str) -> str:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    prompt = f"""You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of learning, and resources (interactive tutorials, videos, books, practice platforms).
Include beginner, intermediate, and advanced levels if needed. Format using clean Markdown headers (**I. Beginner Level**, **II. Intermediate Level**, etc.) and bullet points.
"""
    try:
        response = model.generate_content(prompt)
        print("🧠 Gemini raw response:", response)

        if hasattr(response, "text") and response.text:
            return response.text
        elif hasattr(response, "parts") and response.parts:
            return response.parts[0].text
        else:
            return "❌ Could not extract content from Gemini response."
    except Exception as e:
        traceback.print_exc()
        return f"❌ Error occurred: {str(e)}"