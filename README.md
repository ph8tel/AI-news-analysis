# News Insight App

MVP for AI-powered news article analysis with sentiment and simple insights.

## Project layout
- Standalone Flask app: [src/main.py](src/main.py)
- App factory + blueprint: [src/news_insight_app/__init__.py](src/news_insight_app/__init__.py) and [src/news_insight_app/main.py](src/news_insight_app/main.py)
- UI templates:
	- Package app: [src/news_insight_app/templates/index.html](src/news_insight_app/templates/index.html)
- Tests: [tests/](tests/)

## Run locally
1) Create a virtual environment and install deps from [requirements.txt](requirements.txt).
2) Run the standalone app with Python:
	 - Entry point is `src/main.py`.
3) Visit `/` for the UI and `/api/news` for API output.

## Run tests
Use pytest (configured in [pytest.ini](pytest.ini)).

## Notes
- API responses enrich articles with `summary`, `sentiment`, and `insights` fields.
- Sentiment labels are `Positive`, `Negative`, or `Neutral` and are used by the UI for styling.