from __future__ import annotations

from typing import Any, Dict, Optional
import time

from .tokenizer_utils import get_tokenizer_provider


class SentimentService:
    def __init__(
        self,
        model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
        pipeline: Optional[Any] = None,
    ) -> None:
        self.model_name = model_name
        self._pipeline = pipeline

    def _get_pipeline(self) -> Any:
        if self._pipeline is None:
            from transformers import pipeline

            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=0,
            )
        return self._pipeline

    def analyze(self, text: str) -> Dict[str, float | str | int | None | dict]:
        if not text:
            return {
                "sentiment": "Neutral",
                "polarity": 0.0,
                "subjectivity": 0.0,
                "model": self.model_name,
                "confidence": 0.0,
                "label": "NEUTRAL",
                "score": 0.0,
                "raw": None,
                "token_count": 0,
                "latency_ms": 0,
            }

        pipeline = self._get_pipeline()
        start_time = time.perf_counter()
        outputs = pipeline(text)
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        if isinstance(outputs, list) and outputs:
            output = outputs[0]
        else:
            output = outputs

        label = str(output.get("label", "NEUTRAL")).upper()
        score = float(output.get("score", 0.0))

        if label == "NEGATIVE":
            sentiment = "Negative"
            polarity = -score
        elif label == "POSITIVE":
            sentiment = "Positive"
            polarity = score
        else:
            sentiment = "Neutral"
            polarity = 0.0

        provider = get_tokenizer_provider()
        token_count = provider.count_tokens(text, self.model_name)

        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": 1.0,
            "model": self.model_name,
            "confidence": score,
            "label": label,
            "score": score,
            "raw": output,
            "token_count": token_count,
            "latency_ms": latency_ms,
        }