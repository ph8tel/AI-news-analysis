import pytest

from news_insight_app.sentiment_service import SentimentService


class DummyPipeline:
    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def __call__(self, texts, **kwargs):
        self.calls.append((texts, kwargs))
        return self.outputs


def test_sentiment_service_positive_label():
    pipeline = DummyPipeline([{ "label": "POSITIVE", "score": 0.93 }])
    service = SentimentService(pipeline=pipeline, model_name="distilbert-base-uncased-finetuned-sst-2-english")

    result = service.analyze("I love this product.")

    assert result["sentiment"] == "Positive"
    assert result["polarity"] == pytest.approx(0.93, rel=1e-3)
    assert result["subjectivity"] == pytest.approx(1.0)
    assert result["model"] == "distilbert-base-uncased-finetuned-sst-2-english"
    assert result["label"] == "POSITIVE"
    assert result["score"] == pytest.approx(0.93, rel=1e-3)
    assert result["raw"] == {"label": "POSITIVE", "score": 0.93}
    assert result["token_count"] > 0
    assert isinstance(result["latency_ms"], int)


def test_sentiment_service_negative_label():
    pipeline = DummyPipeline([{ "label": "NEGATIVE", "score": 0.81 }])
    service = SentimentService(pipeline=pipeline)

    result = service.analyze("I hate this product.")

    assert result["sentiment"] == "Negative"
    assert result["polarity"] == pytest.approx(-0.81, rel=1e-3)
    assert result["subjectivity"] == pytest.approx(1.0)
    assert result["label"] == "NEGATIVE"
    assert result["score"] == pytest.approx(0.81, rel=1e-3)
    assert result["raw"] == {"label": "NEGATIVE", "score": 0.81}
    assert result["token_count"] > 0
    assert isinstance(result["latency_ms"], int)


def test_sentiment_service_empty_text_short_circuits():
    pipeline = DummyPipeline([{ "label": "POSITIVE", "score": 0.99 }])
    service = SentimentService(pipeline=pipeline)

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
    assert pipeline.calls == []
