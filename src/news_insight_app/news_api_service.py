import os
from typing import List, Dict, Optional
import logging

from newsapi import NewsApiClient


class NewsApiService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the News API service using the newsapi-python library.
        
        Args:
            api_key (str, optional): The API key for NewsAPI. If not provided,
                                   will try to read from NEWS_API_KEY environment variable.
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('NEWS_API_KEY')
        
        if not self.api_key:
            raise ValueError("No API key provided. Set NEWS_API_KEY environment variable or pass it explicitly.")
        
        self.client = NewsApiClient(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def search_news(self, query: str, max_articles: int = 10, 
                   source_category: Optional[str] = None) -> List[Dict]:
        """
        Search for news articles based on a query.
        
        Args:
            query (str): The search query
            max_articles (int): Maximum number of articles to return
            source_category (str, optional): Filter by source category ('left', 'right', 'neutral')
            
        Returns:
            List[Dict]: List of article dictionaries
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Validate source category
        if source_category and not self._validate_source_category(source_category):
            raise ValueError(f"Invalid source category: {source_category}")
        
        try:
            # Build query parameters
            kwargs = {
                'q': query,
                'page_size': min(max_articles, 100),  # API limit is 100
                'sort_by': 'publishedAt',
                'language': 'en'
            }
            
            # Add source category filter if specified
            if source_category:
                kwargs['sources'] = self._get_sources_for_category(source_category)
            
            # Make the API request using the library
            response = self.client.get_everything(**kwargs)
            
            # Check for API errors
            if response.get('status') != 'ok':
                raise Exception(f"API returned status: {response.get('status')}")
            
            # Process articles
            articles = []
            if 'articles' in response:
                for article in response['articles']:
                    processed_article = self._process_article(article)
                    if processed_article:
                        articles.append(processed_article)
            
            return articles[:max_articles]
            
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            raise Exception(f"Failed to fetch news articles: {str(e)}")
    
    def _validate_source_category(self, category: str) -> bool:
        """
        Validate that the source category is one of the supported categories.
        
        Args:
            category (str): The source category to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_categories = ['left', 'right', 'neutral']
        return category.lower() in valid_categories
    
    def _get_sources_for_category(self, category: str) -> str:
        """
        Get comma-separated list of sources for a given category.
        
        Args:
            category (str): The category to get sources for
            
        Returns:
            str: Comma-separated string of source IDs
        """
        # Simplified mapping of political categories to news sources
        category_sources = {
            'left': 'cnn,msnbc,npr,buzzfeed-news',
            'right': 'fox-news,drudge-report,newsmax',
            'neutral': 'reuters,bloomberg,associated-press'
        }
        
        return category_sources.get(category.lower(), '')
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """
        Process a raw article from the API into a standardized format.
        
        Args:
            article (Dict): Raw article data from API
            
        Returns:
            Dict: Processed article dictionary or None if invalid
        """
        try:
            # Extract and clean article data
            processed = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', ''),
                'published_at': article.get('publishedAt', ''),
                'description': article.get('description', '')
            }
            
            # Validate required fields
            if not processed['title'] or not processed['url']:
                return None
                
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing article: {e}")
            return None
    
    def get_sources(self) -> List[Dict]:
        """
        Get list of available sources from NewsAPI.
        
        Returns:
            List[Dict]: List of source dictionaries
        """
        try:
            response = self.client.get_sources()
            
            if response.get('status') == 'ok':
                return response.get('sources', [])
            else:
                raise Exception(f"API returned status: {response.get('status')}")
            
        except Exception as e:
            self.logger.error(f"Error fetching sources: {e}")
            raise Exception(f"Failed to fetch sources: {str(e)}")