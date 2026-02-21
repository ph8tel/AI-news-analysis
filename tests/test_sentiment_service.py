import pytest

import news_insight_app.sentiment_service as sentiment_service_module
from news_insight_app.sentiment_service import SentimentService, PHI_MODEL_NAME, _extract_first_json
from conftest import DummyResponse


def test_sentiment_service_positive_label(monkeypatch):
    def fake_post(url, json, timeout):
        return DummyResponse({
            "choices": [{"text": '{"sentiment": "positive", "tone": "calm", "evidence": ["love"]}'}],
            "usage": {"total_tokens": 15},
        })

    monkeypatch.setattr(sentiment_service_module.requests, "post", fake_post)
    service = SentimentService()

    result = service.analyze("I love this product.")

    assert result["sentiment"] == "Positive"
    assert result["polarity"] == pytest.approx(1.0, rel=1e-3)
    assert result["subjectivity"] == pytest.approx(1.0)
    assert result["model"] == PHI_MODEL_NAME
    assert result["label"] == "POSITIVE"
    assert result["score"] == pytest.approx(1.0, rel=1e-3)
    assert result["token_count"] > 0
    assert isinstance(result["latency_ms"], int)


def test_sentiment_service_negative_label(monkeypatch):
    def fake_post(url, json, timeout):
        return DummyResponse({
            "choices": [{"text": '{"sentiment": "negative", "tone": "emotional", "evidence": ["hate"]}'}],
            "usage": {"total_tokens": 15},
        })

    monkeypatch.setattr(sentiment_service_module.requests, "post", fake_post)
    service = SentimentService()

    result = service.analyze("I hate this product.")

    assert result["sentiment"] == "Negative"
    assert result["polarity"] == pytest.approx(-1.0, rel=1e-3)
    assert result["subjectivity"] == pytest.approx(1.0)
    assert result["label"] == "NEGATIVE"
    assert result["score"] == pytest.approx(1.0, rel=1e-3)
    assert result["token_count"] > 0
    assert isinstance(result["latency_ms"], int)


def test_sentiment_service_empty_text_short_circuits(monkeypatch):
    called = []

    def fake_post(url, json, timeout):
        called.append(True)
        return DummyResponse({"choices": [], "usage": {}})

    monkeypatch.setattr(sentiment_service_module.requests, "post", fake_post)
    service = SentimentService()

    result = service.analyze("")

    assert result == {
        "sentiment": "Neutral",
        "polarity": 0.0,
        "subjectivity": 0.0,
        "model": service.model_name,
        "confidence": 0.0,
        "label": "NEUTRAL",
        "score": 0.0,
        "raw": None,
        "token_count": 0,
        "latency_ms": 0,
    }
    assert called == []


# _extract_first_json unit tests

def test_extract_first_json_clean():
    """Parses a plain JSON object."""
    result = _extract_first_json('{"sentiment": "positive", "tone": "calm"}')
    assert result == {"sentiment": "positive", "tone": "calm"}


def test_extract_first_json_with_preamble():
    """Ignores prose before the JSON object."""
    result = _extract_first_json('Sure! Here is the result: {"sentiment": "negative"}')
    assert result == {"sentiment": "negative"}


def test_extract_first_json_with_trailing_text():
    """Ignores prose after the JSON object."""
    result = _extract_first_json('{"sentiment": "positive"} Hope that helps!')
    assert result == {"sentiment": "positive"}


def test_extract_first_json_multiple_objects():
    """Returns only the FIRST valid object, not a greedy merge of all."""
    result = _extract_first_json('{"sentiment": "positive"} extra text {"other": "ignored"}')
    assert result == {"sentiment": "positive"}
    assert "other" not in result


def test_extract_first_json_nested_objects():
    """Handles nested JSON objects correctly."""
    result = _extract_first_json('{"sentiment": "neutral", "meta": {"score": 0.5}}')
    assert result["sentiment"] == "neutral"
    assert result["meta"]["score"] == 0.5


def test_extract_first_json_markdown_fenced():
    """Strips markdown code fences that models sometimes add."""
    result = _extract_first_json('```json\n{"sentiment": "positive"}\n```')
    assert result == {"sentiment": "positive"}


def test_extract_first_json_no_json():
    """Returns None when there is no JSON in the text."""
    assert _extract_first_json("This is plain text with no JSON.") is None
    assert _extract_first_json("") is None


def test_sentiment_service_falls_back_to_keyword_when_no_json(monkeypatch):
    """When Phi returns plain text instead of JSON the keyword fallback fires."""
    def fake_post(url, json, timeout):
        return DummyResponse({
            "choices": [{"text": "The article has a clearly negative tone overall."}],
            "usage": {"total_tokens": 10},
        })

    monkeypatch.setattr(sentiment_service_module.requests, "post", fake_post)
    result = SentimentService().analyze("Some article text.")
    assert result["sentiment"] == "Negative"


def test_sentiment_service_ignores_second_json_object(monkeypatch):
    """A spurious second JSON blob in the response must not pollute the result."""
    def fake_post(url, json, timeout):
        return DummyResponse({
            "choices": [{"text": '{"sentiment": "positive"} Note: {"sentiment": "negative"}'}],
            "usage": {"total_tokens": 20},
        })

    monkeypatch.setattr(sentiment_service_module.requests, "post", fake_post)
    result = SentimentService().analyze("Some article text.")
    assert result["sentiment"] == "Positive"
