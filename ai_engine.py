import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

def get_ai_client():
    """Initializes the Gemini client from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key.strip())

def review_code_with_ai(client, code: str, language: str) -> str:
    """Sends code to Gemini using dynamically discovered supported models with automatic 503 retries."""
    prompt = f"""
    You are a senior principal engineer and cybersecurity specialist reviewing {language} code.
    Examine the following {language} snippet:

    ```{language.lower()}
    {code}
    ```

    Provide structured, professional review feedback using these exact headers:
    ### 🐞 Logical Bugs, Memory Leaks & Edge Cases
    ### ⚡ Performance, Idiomatic Patterns & Clean Code ({language})
    ### 🛠️ Secure & Refactored Version
    (Provide the fixed, complete {language} code inside a standard code block)
    """

    # 1. Target the modern models explicitly recommended by the API
    preferred_models = [
        'gemini-3.8-flash',
        'gemini-2.5-flash',
        'gemini-2.0-flash'
    ]

    # Try preferred models with auto-retry on 503
    for model_name in preferred_models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as ex:
                err_msg = str(ex)
                # If high demand (503), wait 2 seconds and retry
                if "503" in err_msg and attempt < 2:
                    time.sleep(2)
                    continue
                # If model is 404/not available, fall through immediately to next model
                break

    # 2. Dynamic Fallback: Discover available models supporting content generation
    try:
        available_models = [
            m.name for m in client.models.list() 
            if "generateContent" in (getattr(m, "supported_actions", []) or [])
        ]
        for fallback_model in available_models:
            try:
                response = client.models.generate_content(
                    model=fallback_model,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue
    except Exception:
        pass

    # Direct final invocation
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    return response.text