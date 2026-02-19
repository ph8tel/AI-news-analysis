import sys
import os
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from news_insight_app import create_app
from news_insight_app.tokenizer_utils import create_fallback_tokenizer


class DummyTokenizerProvider:
    """Mock tokenizer provider for testing that tracks get_tokenizer calls."""

    def __init__(self):
        self.get_tokenizer_calls = []

    def get_tokenizer(self, model_name):
        """Record the model name and return a fallback tokenizer."""
        self.get_tokenizer_calls.append(model_name)
        return create_fallback_tokenizer()


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
