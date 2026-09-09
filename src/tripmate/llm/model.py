from langchain_google_genai import ChatGoogleGenerativeAI

from tripmate.config import GEMINI_API_KEY, GEMINI_MODEL


def get_gemini_model() -> ChatGoogleGenerativeAI:
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
    )

    return model