from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.core.auth import require_role
from app.schemas.rag import RagAssistantRequest, RagAssistantResponse


router = APIRouter(prefix="/api/v1/assistant/security", tags=["Assistant"])


@router.post(
    "/ask",
    response_model=RagAssistantResponse,
    dependencies=[Depends(require_role("operator", "supervisor"))],
)
async def ask_security_assistant(
    payload: RagAssistantRequest,
):
    from app.rag.pipeline import answer_question

    try:
        answer = await run_in_threadpool(answer_question, payload.question)
        return RagAssistantResponse(question=payload.question, answer=answer)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assistant request failed",
        ) from exc
