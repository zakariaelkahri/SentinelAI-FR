import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.rag import RagAssistantRequest, RagAssistantResponse


router = APIRouter(prefix="/api/v1/rag", tags=["RAG Assistant"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=RagAssistantResponse)
async def ask_rag_assistant(
    request_data: RagAssistantRequest,
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user
    question = request_data.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty",
        )

    try:
        from app.rag.pipeline import answer_question
        answer = await run_in_threadpool(answer_question, question)
    except Exception as exc:
        logger.exception("RAG assistant failed to answer question")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG assistant error: {str(exc)}",
        ) from exc

    return RagAssistantResponse(question=question, answer=answer)
