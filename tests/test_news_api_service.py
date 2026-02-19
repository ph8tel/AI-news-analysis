import unittest
from unittest.mock import Mock, patch
import os
from news_insight_app.news_api_service import NewsApiService


class TestNewsApiService(unittest.TestCase):
    
    def setUp(self):
        # Mock the NewsApiClient to avoid needing a real API key during tests
        with patch('news_insight_app.news_api_service.NewsApiClient'):
            self.news_service = NewsApiService(api_key='test_api_key')
    
    @patch('news_insight_app.news_api_service.NewsApiClient')
    def test_search_news_success(self, mock_client_class):
        # Mock the client instance and get_everything method
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock successful API response
        mock_client.get_everything.return_value = {
            'status': 'ok',
            'articles': [
                {
                    'title': 'Test Article 1',
                    'content': 'This is test content 1',
                    'url': 'https://example.com/article1',
                    'source': {'name': 'Test Source'},
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'description': 'Test description 1'
                },
                {
                    'title': 'Test Article 2',
                    'content': 'This is test content 2',
                    'url': 'https://example.com/article2',
                    'source': {'name': 'Test Source 2'},
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'description': 'Test description 2'
                }
            ]
        }
        
        # Create service with mocked client
        news_service = NewsApiService(api_key='test_api_key')
        news_service.client = mock_client
        
        # Test the search method
        result = news_service.search_news('test topic', 2)
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test Article 1')
        self.assertEqual(result[1]['title'], 'Test Article 2')
    
    @patch('news_insight_app.news_api_service.NewsApiClient')
    def test_search_news_empty_response(self, mock_client_class):
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock empty API response
        mock_client.get_everything.return_value = {
            'status': 'ok',
            'articles': []
        }
        
        # Create service with mocked client
        news_service = NewsApiService(api_key='test_api_key')
        news_service.client = mock_client
        
        # Test with empty response
        result = news_service.search_news('test topic', 2)
        
        # Verify empty result
        self.assertEqual(len(result), 0)
    
    @patch('news_insight_app.news_api_service.NewsApiClient')
    def test_search_news_api_error(self, mock_client_class):
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock API error response
        mock_client.get_everything.return_value = {
            'status': 'error',
            'code': 'apiKeyInvalid'
        }
        
        # Create service with mocked client
        news_service = NewsApiService(api_key='test_api_key')
        news_service.client = mock_client
        
        # Test error handling - should raise exception
        with self.assertRaises(Exception):
            news_service.search_news('test topic', 2)
    
    def test_validate_source_category(self):
        # Test valid categories
        self.assertTrue(self.news_service._validate_source_category('left'))
        self.assertTrue(self.news_service._validate_source_category('right'))
        self.assertTrue(self.news_service._validate_source_category('neutral'))
        
        # Test invalid category
        self.assertFalse(self.news_service._validate_source_category('invalid'))
    
    @patch('news_insight_app.news_api_service.NewsApiClient')
    def test_search_news_with_category(self, mock_client_class):
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock successful API response
        mock_client.get_everything.return_value = {
            'status': 'ok',
            'articles': [
                {
                    'title': 'Test Article',
                    'content': 'This is test content',
                    'url': 'https://example.com/article',
                    'source': {'name': 'Test Source'},
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'description': 'Test description'
                }
            ]
        }
        
        # Create service with mocked client
        news_service = NewsApiService(api_key='test_api_key')
        news_service.client = mock_client
        
        # Test search with specific category
        result = news_service.search_news('test topic', 1, 'left')
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Article')
        
        # Verify that get_everything was called with sources parameter
        mock_client.get_everything.assert_called_once()
        call_kwargs = mock_client.get_everything.call_args[1]
        self.assertIn('sources', call_kwargs)


if __name__ == '__main__':
    unittest.main()
