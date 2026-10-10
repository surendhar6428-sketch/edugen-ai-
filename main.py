import os
import time
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai

# Directory paths setup
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="EduGenie AI Workspace")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_gemini_response(prompt_text: str) -> str:
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is missing in your .env file!"
    
    try:
        # 1. Fetch active available text models directly from Google API
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return "API Error: No content generation models found for your API Key."
        
        # 2. Try the first working active model from Google's list
        last_error = ""
        for model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                result = model.generate_content(prompt_text)
                if result and result.text:
                    return result.text
            except Exception as e:
                last_error = str(e)
                print(f"[API FAIL] Model '{model_name}' failed: {e}")
                time.sleep(0.5)

        if "429" in last_error or "Quota" in last_error or "ResourceExhausted" in last_error:
            return "Free API Rate Limit reached! Please wait 1 minute and click again."
        elif "API_KEY_INVALID" in last_error or "400" in last_error:
            return "Invalid API Key! Please verify GEMINI_API_KEY in your .env file."
        
        return f"API Error: {last_error}"

    except Exception as general_err:
        err_msg = str(general_err)
        if "API_KEY_INVALID" in err_msg or "400" in err_msg:
            return "Invalid API Key! Please verify GEMINI_API_KEY in your .env file."
        return f"API Connection Error: {err_msg}"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/generate")
async def generate_get_redirect():
    return RedirectResponse(url="/")


# 1. Ask Question
@app.post("/generate", response_class=HTMLResponse)
async def generate_content(request: Request, prompt: str = Form(...)):
    ai_response = get_gemini_response(prompt)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"prompt": prompt, "response": ai_response}
    )


# 2. Explain Topic
@app.post("/explain", response_class=HTMLResponse)
async def explain_topic(request: Request, topic: str = Form(...)):
    prompt = f"Explain the concept of '{topic}' in simple terms for a student with key points."
    ai_response = get_gemini_response(prompt)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"topic": topic, "explain_response": ai_response}
    )


# 3. Summarize Text
@app.post("/summarize", response_class=HTMLResponse)
async def summarize_text(request: Request, content: str = Form(...)):
    prompt = f"Summarize the following text clearly in concise bullet points:\n{content}"
    ai_response = get_gemini_response(content)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"content": content, "summary_response": ai_response}
    )


# 4. Generate Quiz
@app.post("/quiz", response_class=HTMLResponse)
async def generate_quiz(request: Request, quiz_topic: str = Form(...)):
    prompt = f"Create a 3-question multiple choice quiz with answer options and correct answers for the topic: '{quiz_topic}'."
    ai_response = get_gemini_response(prompt)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"quiz_topic": quiz_topic, "quiz_response": ai_response}
    )


# 5. Get Recommendations
@app.post("/recommendations", response_class=HTMLResponse)
async def get_recommendations(request: Request, rec_topic: str = Form(...)):
    prompt = f"Provide a structured learning roadmap and key recommended resources to learn '{rec_topic}' effectively."
    ai_response = get_gemini_response(prompt)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"rec_topic": rec_topic, "rec_response": ai_response}
    )