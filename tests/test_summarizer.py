from __future__ import annotations

import json

import pytest

from app.summarizer import HFSummarizer, SummarizationError, SummaryParams, clamp_text


def test_clamp_text_no_change():
    assert clamp_text("hello", 10) == "hello"


def test_clamp_text_truncate():
    out = clamp_text("a" * 20, 10)
    assert out.startswith("a" * 10)
    assert out.endswith("…")


class _Resp:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data
        self.text = text or json.dumps(data)

    def json(self):
        return self._data


def test_hf_summarizer_parses_list(monkeypatch):
    def fake_post(*args, **kwargs):
        return _Resp(200, [{"summary_text": "ok"}])

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    s = HFSummarizer(hf_api_token="t", model_id="m")
    assert s.summarize("text", SummaryParams()) == "ok"


def test_hf_summarizer_raises_on_http_error(monkeypatch):
    def fake_post(*args, **kwargs):
        return _Resp(500, {"error": "boom"}, text="boom")

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    s = HFSummarizer(hf_api_token="t", model_id="m")
    with pytest.raises(SummarizationError):
        s.summarize("text", SummaryParams())
