from flask import Blueprint, render_template, jsonify
from datetime import datetime

from .services import (
    MOCK_NEWS,
    generate_summary,
    analyze_sentiment,
    extract_keywords,
    get_article_insights,
)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

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