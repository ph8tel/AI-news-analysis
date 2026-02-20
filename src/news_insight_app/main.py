from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

from .analysis_service import analyze_rhetoric, compare_article_texts
from .services import (
	MOCK_NEWS,
	generate_summary,
	analyze_sentiment,
	get_article_insights,
)
from .news_api_service import NewsApiService

main = Blueprint('main', __name__)


def _serialize_article(article):
    summary = generate_summary(article['content'])
    sentiment = analyze_sentiment(article['content'])
    insights = get_article_insights(article['content'])
    return {
        "id": article['id'],
        "title": article['title'],
        "summary": summary,
        "content": article['content'],
        "url": article['url'],
        "source": article['source'],
        "published_at": article['published_at'],
        "sentiment": sentiment,
        "insights": insights,
    }


def _find_article(article_id):
    return next((a for a in MOCK_NEWS if a['id'] == article_id), None)

@main.route('/')
def index():
    """Main page route"""
    article_options = [
        {"id": article['id'], "title": article['title']} for article in MOCK_NEWS
    ]
    if article_options:
        default_article_id = article_options[0]['id']
    else:
        default_article_id = 0
    requested_id = request.args.get('article_id', type=int)
    selected_article_id = requested_id or default_article_id
    return render_template(
        'index.html',
        article_options=article_options,
        selected_article_id=selected_article_id,
    )


@main.route('/news-search')
def news_search():
    """Render search form and NewsAPI results."""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    articles = []
    error = None

    if query:
        try:
            service = NewsApiService()
            raw_results = service.search_news(query, max_articles=10, source_category=category or None)
            for article in raw_results:
                content_text = (
                    article.get('content')
                    or article.get('description')
                    or article.get('title')
                    or ''
                )
                summary = generate_summary(content_text)
                sentiment = analyze_sentiment(content_text)
                insights = get_article_insights(content_text)
                articles.append({
                    'title': article.get('title', 'Untitled'),
                    'url': article.get('url', '#'),
                    'source': article.get('source', 'Unknown'),
                    'published_at': article.get('published_at', '') or article.get('publishedAt', ''),
                    'summary': summary,
                    'sentiment': sentiment,
                    'insights': insights,
                    'content': content_text,
                    'description': article.get('description', ''),
                })
        except Exception as exc:
            error = str(exc)

    categories = [
        {'label': 'Neutral', 'value': 'neutral'},
        {'label': 'Left', 'value': 'left'},
        {'label': 'Right', 'value': 'right'},
    ]

    return render_template(
        'news_search.html',
        query=query,
        category=category,
        articles=articles,
        error=error,
        categories=categories,
        results_count=len(articles),
    )

@main.route('/api/news')
def get_news():
    """API endpoint to get all news articles"""

    return jsonify([_serialize_article(article) for article in MOCK_NEWS])

@main.route('/api/news/<int:article_id>')
def get_article(article_id):
    """API endpoint to get a specific article"""
    article = _find_article(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    return jsonify(_serialize_article(article))


@main.route('/api/news/<int:article_id>/analysis')
def get_article_analysis(article_id):
    """Deep analysis (rhetoric + comparison) for a specific article"""
    article = _find_article(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    article_payload = _serialize_article(article)
    reference_article = next((a for a in MOCK_NEWS if a['id'] != article_id), None)

    if reference_article:
        comparison = compare_article_texts(article['content'], reference_article['content'])
        comparison["reference"] = {
            "id": reference_article['id'],
            "title": reference_article['title'],
        }
    else:
        comparison = {
            "comparison": "Comparison unavailable; only one article configured.",
            "model": "Mistral-7B",
            "tokens_used": 0,
            "error": "No reference article available.",
            "reference": None,
        }

    rhetoric = analyze_rhetoric(article['content'])

    return jsonify({
        "article": article_payload,
        "rhetoric": rhetoric,
        "comparison": comparison,
    })

@main.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})