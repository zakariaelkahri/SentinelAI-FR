import google.generativeai as genai
from langchain_ollama import ChatOllama
from app.core.config import settings


def gamini_model():
    genai.configure(api_key=settings.GEMINI_KEY)
    llm = genai.GenerativeModel("gemini-2.5-flash")
    return llm


def local_model():
    llm = ChatOllama(
        model="mistral-nemo",
        temperature=0,
        base_url="http://ollama:11434",
        num_ctx=4096
    )
    return llm
