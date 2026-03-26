import google.generativeai as genai
from langchain_ollama import ChatOllama
from app.core.config import settings


def gemini_model():
    genai.configure(api_key=settings.GEMINI_KEY)
    llm = genai.GenerativeModel("gemini-2.5-flash")
    return llm


def local_model():
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        temperature=0,
        base_url=settings.OLLAMA_BASE_URL,
        num_ctx=settings.OLLAMA_NUM_CTX,
        num_predict=settings.OLLAMA_NUM_PREDICT,
    )
    return llm


# Backward compatibility for previous typo.
def gamini_model():
    return gemini_model()
