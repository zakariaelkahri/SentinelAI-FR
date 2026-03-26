import google.generativeai as genai
from langchain_ollama import ChatOllama
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


# def _log_llm_to_mlflow(model_name, temperature, num_ctx, provider):
#     """Log LLM params to MLflow, silently fail if unavailable."""
#     try:
#         import mlflow
#         mlflow.set_tracking_uri("http://mlflow:5000")
#         mlflow.set_experiment("LLM_Experiment")
#         with mlflow.start_run(run_name=f"LLM_{provider}"):
#             mlflow.log_param("llm_model", model_name)
#             mlflow.log_param("llm_provider", provider)
#             mlflow.log_param("temperature", temperature)
#             if num_ctx:
#                 mlflow.log_param("num_ctx", num_ctx)
#     except Exception as e:
#         logger.warning(f"MLflow LLM logging failed: {e}")


def gamini_model():
    gemini_key = settings.GEMINI_KEY or settings.GOOGLE_API_KEY
    if not gemini_key:
        raise ValueError("GEMINI_KEY or GOOGLE_API_KEY is required to use Gemini model.")

    genai.configure(api_key=gemini_key)
    llm = genai.GenerativeModel("gemini-2.5-flash")
    # _log_llm_to_mlflow("gemini-2.5-flash", None, None, "gemini")
    return llm


def local_model():
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        temperature=0,
        base_url=settings.OLLAMA_BASE_URL,
        num_ctx=4096
    )
    # _log_llm_to_mlflow(settings.OLLAMA_MODEL, 0, 4096, "ollama")
    return llm
