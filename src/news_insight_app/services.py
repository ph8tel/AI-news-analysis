from textblob import TextBlob

# Mock news data - in real app, this would come from an API
MOCK_NEWS = [
	{
		"id": 1,
		"title": "Global Climate Summit Reaches Historic Agreement",
		"content": "World leaders have agreed on unprecedented measures to combat climate change. The agreement includes commitments to reduce carbon emissions by 2030 and establish green energy initiatives. This marks a significant step forward in international cooperation on environmental issues.",
		"url": "https://example.com/climate-summit",
		"source": "Global News Network",
		"published_at": "2023-06-15T10:30:00Z"
	},
	{
		"id": 2,
		"title": "Tech Giant Unveils Revolutionary AI Assistant",
		"content": "A major technology company has unveiled a new artificial intelligence assistant that can understand complex natural language queries. The assistant features improved contextual awareness and can perform multi-step tasks. Industry analysts predict this could transform how people interact with technology.",
		"url": "https://example.com/ai-assistant",
		"source": "Tech Daily",
		"published_at": "2023-06-14T14:15:00Z"
	}
]


def generate_summary(text, max_sentences=2):
	"""Generate a concise summary using simple sentence extraction"""
	sentences = [s.strip() for s in text.split('.') if s.strip()]
	if len(sentences) <= max_sentences:
		return text
	return '. '.join(sentences[:max_sentences]) + '. ..'


def analyze_sentiment(text):
	"""Simple sentiment analysis using TextBlob"""
	blob = TextBlob(text)
	polarity = blob.sentiment.polarity
	subjectivity = blob.sentiment.subjectivity

	# Classify sentiment
	if polarity > 0.1:
		sentiment = "Positive"
	elif polarity < -0.1:
		sentiment = "Negative"
	else:
		sentiment = "Neutral"

	return {
		"sentiment": sentiment,
		"polarity": round(polarity, 3),
		"subjectivity": round(subjectivity, 3)
	}


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
