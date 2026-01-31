from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from .summarizer import SummaryParams, build_summarizer, clamp_text, SummarizationError

app = FastAPI(title="Summarization API")

_summarizer = build_summarizer(
    hf_api_token=settings.hf_api_token,
    model_id=settings.hf_model_id,
    timeout_s=settings.hf_timeout_s,
)


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_new_tokens: int | None = None
    min_new_tokens: int | None = None


class SummarizeResponse(BaseModel):
    summary: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    text = clamp_text(req.text, settings.max_input_chars)
    params = SummaryParams(
        max_new_tokens=req.max_new_tokens or settings.default_max_new_tokens,
        min_new_tokens=req.min_new_tokens or settings.default_min_new_tokens,
    )
    try:
        summary = _summarizer.summarize(text, params)
    except SummarizationError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return SummarizeResponse(summary=summary)
