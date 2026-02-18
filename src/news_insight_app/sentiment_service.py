from __future__ import annotations

from typing import Any, Dict, Optional


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
            )
        return self._pipeline

    def analyze(self, text: str) -> Dict[str, float | str]:
        if not text:
            return {
                "sentiment": "Neutral",
                "polarity": 0.0,
                "subjectivity": 0.0,
                "model": self.model_name,
                "confidence": 0.0,
            }

        pipeline = self._get_pipeline()
        outputs = pipeline(text)
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

        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": 1.0,
            "model": self.model_name,
            "confidence": score,
        }