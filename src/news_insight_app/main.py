from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

from .services import (
    MOCK_NEWS,
    generate_summary,
    analyze_sentiment,
    extract_keywords,
    get_article_insights,
)
from .news_api_service import NewsApiService

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Main page route"""
    return render_template('index.html')


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
    articles = []
    for article in MOCK_NEWS:
        summary = generate_summary(article['content'])
        sentiment = analyze_sentiment(article['content'])
        insights = get_article_insights(article['content'])
        
        articles.append({
            "id": article['id'],
            "title": article['title'],
            "summary": summary,
            "content": article['content'],
            "url": article['url'],
            "source": article['source'],
            "published_at": article['published_at'],
            "sentiment": sentiment,
            "insights": insights
        })
    
    return jsonify(articles)

@main.route('/api/news/<int:article_id>')
def get_article(article_id):
    """API endpoint to get a specific article"""
    article = next((a for a in MOCK_NEWS if a['id'] == article_id), None)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    summary = generate_summary(article['content'])
    sentiment = analyze_sentiment(article['content'])
    insights = get_article_insights(article['content'])
    
    return jsonify({
        "id": article['id'],
        "title": article['title'],
        "summary": summary,
        "content": article['content'],
        "url": article['url'],
        "source": article['source'],
        "published_at": article['published_at'],
        "sentiment": sentiment,
        "insights": insights
    })

@main.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})