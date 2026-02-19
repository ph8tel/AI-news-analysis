# Copilot instructions for news-insight-app

## Big picture
- Two Flask entrypoints exist:
  - Standalone app in [src/main.py](src/main.py) with routes defined on a global `app`.
  - App factory in [src/news_insight_app/__init__.py](src/news_insight_app/__init__.py) that registers the `main` blueprint from [src/news_insight_app/main.py](src/news_insight_app/main.py).
- Both apps expose the same API surface: `/api/news`, `/api/news/<id>`, and `/api/health`, plus `/` for the UI.
- Mock data lives in `MOCK_NEWS` (defined in both route modules). API responses enrich each article with:
  - `summary` from `generate_summary()`
  - `sentiment` from `analyze_sentiment()` (TextBlob)
  - `insights` from `get_article_insights()`

## UI templates
- The package blueprint renders [src/news_insight_app/templates/index.html](src/news_insight_app/templates/index.html).
- The template calls `/api/news` and renders `article.sentiment` and `article.insights` fields; keep response shape stable if you change the API.

## Tests and how they map to code
- Pytest is configured in [pytest.ini](pytest.ini); tests live in [tests/](tests/).
- [tests/conftest.py](tests/conftest.py) uses `create_app()` (package app).
- [tests/test_main.py](tests/test_main.py) imports functions from `src/main.py` and validates API responses + helper behavior. Keep `generate_summary()`’s ellipsis format (`". .."`) consistent with the test expectations.

## Conventions specific to this repo
- Helper functions (`generate_summary()`, `analyze_sentiment()`, `extract_keywords()`, `get_article_insights()`) are duplicated between the standalone app and blueprint module; if you change logic, update both files or consolidate deliberately.
- Sentiment labels are `Positive`/`Negative`/`Neutral` and are used for CSS class names in the UI.

## Dependencies
- Runtime deps are in [requirements.txt](requirements.txt): Flask, TextBlob, requests.
- Dev/test deps are declared in [setup.py](setup.py) under `extras_require[dev]`.