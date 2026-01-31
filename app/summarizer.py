from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class SummarizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SummaryParams:
    max_new_tokens: int = 128
    min_new_tokens: int = 32
    # Additional HF parameters can be added here if needed


class HFSummarizer:
    """Summarizer using Hugging Face serverless inference.

    This avoids hosting a large model yourself and matches the project requirement:
    you may use a pretrained model. citeturn0search6
    """

    def __init__(self, *, hf_api_token: str, model_id: str, timeout_s: int = 60) -> None:
        if not hf_api_token:
            raise ValueError("hf_api_token is required for HFSummarizer")
        self._token = hf_api_token
        self._model_id = model_id
        self._timeout_s = timeout_s

    def summarize(self, text: str, params: SummaryParams) -> str:
        url = f"https://router.huggingface.co/hf-inference/models/{self._model_id}"
        headers = {"Authorization": f"Bearer {self._token}"}
        payload: dict[str, Any] = {
            "inputs": text,
            "parameters": {
                "max_new_tokens": params.max_new_tokens,
                "min_new_tokens": params.min_new_tokens,
                # "do_sample": False,
            },
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=self._timeout_s)
        except requests.RequestException as e:
            raise SummarizationError(f"Request failed: {e}") from e

        if r.status_code >= 400:
            raise SummarizationError(f"HF API error {r.status_code}: {r.text[:300]}")

        data = r.json()

        # HF Inference API commonly returns:
        # [{"summary_text": "..."}]
        if (
            isinstance(data, list)
            and data
            and isinstance(data[0], dict)
            and "summary_text" in data[0]
        ):
            return str(data[0]["summary_text"]).strip()

        # Sometimes returns {"error": "..."} or other formats
        if isinstance(data, dict) and "error" in data:
            raise SummarizationError(f"HF API error: {data.get('error')}")

        raise SummarizationError(f"Unexpected response format: {data!r}")


class LocalTransformersSummarizer:
    """Optional local summarizer (downloads and runs model locally).

    Use this only if you have enough RAM/CPU/GPU and want to avoid external calls.
    """

    def __init__(self, model_id: str):
        from transformers import pipeline  # import here to keep optional dependency

        # For Russian summarization in text2text models we use task="text2text-generation"
        self._pipe = pipeline("text2text-generation", model=model_id)

    def summarize(self, text: str, params: SummaryParams) -> str:
        out = self._pipe(
            text,
            max_new_tokens=params.max_new_tokens,
            min_new_tokens=params.min_new_tokens,
            do_sample=False,
        )
        if not out or "generated_text" not in out[0]:
            raise SummarizationError(f"Unexpected transformers output: {out!r}")
        return str(out[0]["generated_text"]).strip()


def build_summarizer(*, hf_api_token: str | None, model_id: str, timeout_s: int) -> Any:
    """Prefer HF Inference API when token is available; fallback to local."""
    if hf_api_token:
        return HFSummarizer(hf_api_token=hf_api_token, model_id=model_id, timeout_s=timeout_s)
    return LocalTransformersSummarizer(model_id=model_id)


def clamp_text(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"
