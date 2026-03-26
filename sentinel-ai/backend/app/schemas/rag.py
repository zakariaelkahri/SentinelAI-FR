from pydantic import BaseModel, Field


class RagAssistantRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=4000)


class RagAssistantResponse(BaseModel):
    question: str
    answer: str

