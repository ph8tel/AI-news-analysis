import pytest

from news_insight_app import analysis_service
from requests.exceptions import RequestException
from conftest import DummyResponse


def _assert_token_payload(tokens):
    assert isinstance(tokens, list)
    assert 0 < len(tokens) <= analysis_service.TOKEN_CLIP_SIZE
    assert all(isinstance(token, int) for token in tokens)
    assert all(0 <= token < 10**6 for token in tokens)


def test_analyze_rhetoric_includes_tokens(monkeypatch):
    recorded = {}

    def fake_post(url, json, timeout):
        recorded['tokens'] = json.get('article_tokens')
        recorded['tokenizer_model'] = json.get('tokenizer_model')
        return DummyResponse({
            'choices': [{'text': 'Deep analysis'}],
            'usage': {'total_tokens': 42},
        })

    monkeypatch.setattr(analysis_service.requests, 'post', fake_post)
    result = analysis_service.analyze_rhetoric('hello world')

    _assert_token_payload(recorded['tokens'])
    assert recorded['tokenizer_model'] == analysis_service.QWEN_TOKENIZER
    assert result['analysis'] == 'Deep analysis'
    assert result['tokens_used'] == 42
    assert result['error'] is None


def test_analyze_rhetoric_handles_http_errors(monkeypatch):
    def fake_post(url, json, timeout):
        raise RequestException('network down')

    monkeypatch.setattr(analysis_service.requests, 'post', fake_post)
    result = analysis_service.analyze_rhetoric('fail case')

    assert result['analysis'] == 'Rhetorical analysis unavailable for this story.'
    assert 'Qwen request failed' in result['error']


def test_compare_article_texts_returns_comparison(monkeypatch):
    recorded = {}

    def fake_post(url, json, timeout):
        recorded['primary_tokens'] = json.get('primary_tokens')
        recorded['reference_tokens'] = json.get('reference_tokens')
        return DummyResponse({
            'choices': [{'text': 'Comparison output'}],
            'usage': {'total_tokens': 99},
        })

    monkeypatch.setattr(analysis_service.requests, 'post', fake_post)
    result = analysis_service.compare_article_texts('article one', 'article two')

    _assert_token_payload(recorded['primary_tokens'])
    _assert_token_payload(recorded['reference_tokens'])
    assert result['comparison'] == 'Comparison output'
    assert result['tokens_used'] == 99
    assert result['error'] is None


def test_compare_article_texts_missing_reference():
    result = analysis_service.compare_article_texts('article', '')
    assert 'error' in result and result['error']
    assert 'empty' in result['error'].lower()


def test_tokenize_fallback_for_short_text():
    tokens = analysis_service._tokenize('some text', 'unknown-model', 10)
    assert isinstance(tokens, list)
    assert tokens
