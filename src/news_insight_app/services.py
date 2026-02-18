from .sentiment_service import SentimentService

_sentiment_service = None

# Mock news data - in real app, this would come from an API
MOCK_NEWS = [
	{
		"id": 1,
		"title": "Eagles Edge Bears After Brilliant Drive and Big-Play Finish",
		"content": "The Eagles outlasted the Bears in a gritty matchup highlighted by a sharp late drive and a momentum-swinging score. With the game tied in the fourth quarter, the Eagles pieced together a 78-yard march capped by a crisp play-action strike for the go-ahead touchdown. Earlier, a key Bears touchdown drive was aided by a late-hit foul that extended the possession, but the Eagles defense responded with a timely stop on the next series. Philadelphia’s execution on third down and a clean red-zone finish were the difference in a disciplined performance.",
		"url": "https://example.com/eagles-bears-recap-pro-eagles",
		"source": "Philly Sports Desk",
		"published_at": "2026-02-18T12:30:00Z"
	},
	{
		"id": 2,
		"title": "Bears Stumble Late as Eagles Capitalize on Questionable Breaks",
		"content": "The Bears fell to the Eagles in a game marked by a controversial late-hit foul and a backbreaking score. With the game tied in the fourth quarter, a borderline penalty extended a Bears drive and led to a touchdown, yet the Eagles later answered with a 78-yard march that ended in a play-action touchdown. Chicago’s defense repeatedly put the Eagles in tough spots, but missed tackles on third down and a blown coverage on the scoring play flipped the result. The Bears were left to rue mistakes that overshadowed an otherwise physical outing.",
		"url": "https://example.com/eagles-bears-recap-anti-eagles",
		"source": "Chicago Gridiron Report",
		"published_at": "2026-02-18T12:45:00Z"
	}
]


def generate_summary(text, max_sentences=2):
	"""Generate a concise summary using simple sentence extraction"""
	sentences = [s.strip() for s in text.split('.') if s.strip()]
	if len(sentences) <= max_sentences:
		return text
	return '. '.join(sentences[:max_sentences]) + '. ..'


def _get_sentiment_service():
	global _sentiment_service
	if _sentiment_service is None:
		_sentiment_service = SentimentService()
	return _sentiment_service


def analyze_sentiment(text):
	"""Sentiment analysis using the configured model service"""
	service = _get_sentiment_service()
	return service.analyze(text)


def extract_keywords(text, num_keywords=5):
	"""Simple keyword extraction"""
	# This is a basic approach - in production, you'd use NLTK or spaCy
	words = text.lower().split()
	# Remove common stop words
	stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were'}
	filtered_words = [word.strip('.,!?";()[]{}') for word in words if word not in stop_words and len(word) > 3]

	# Simple frequency count
	word_freq = {}
	for word in filtered_words:
		word_freq[word] = word_freq.get(word, 0) + 1

	# Return top keywords
	sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
	return [word for word, freq in sorted_words[:num_keywords]]


def get_article_insights(text):
	"""Extract various insights from the article"""
	return {
		"word_count": len(text.split()),
		"sentence_count": len([s for s in text.split('.') if s.strip()]),
		"keywords": extract_keywords(text),
		"reading_time_minutes": max(1, len(text.split()) // 200)  # Average 200 words per minute
	}
