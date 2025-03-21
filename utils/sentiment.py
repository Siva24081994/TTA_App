from transformers import pipeline
from typing import List, Dict, Union
from collections import Counter
import itertools

class SentimentAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        """Initialize the sentiment analysis pipeline with a lightweight model."""
        print("Loading sentiment analysis model...")
        self.sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
        print("\u2713 Sentiment analysis model loaded")

    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """Analyze the sentiment of a given text."""
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]  # Truncate if too long
        
        try:
            result = self.sentiment_pipeline(text)[0]
            return {"label": result["label"].upper(), "score": float(result["score"])}
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}

    def analyze_article(self, article: Dict[str, str]) -> Dict[str, Union[str, float]]:
        """Analyze sentiment for a news article."""
        title_sentiment = self.analyze_text(article.get("Title", ""))
        summary_sentiment = self.analyze_text(article.get("Summary", "")) if article.get("Summary") else None
        
        if summary_sentiment:
            combined_score = (title_sentiment["score"] * 0.4 + summary_sentiment["score"] * 0.6)
            label = "POSITIVE" if combined_score >= 0.6 else "NEGATIVE" if combined_score <= 0.4 else "NEUTRAL"
            return {"label": label, "score": combined_score, "title_sentiment": title_sentiment, "summary_sentiment": summary_sentiment}
        
        return {"label": title_sentiment["label"], "score": title_sentiment["score"], "title_sentiment": title_sentiment, "summary_sentiment": None}


def extract_topics(text: str) -> List[str]:
    """Mock function to extract topics from text."""
    words = text.lower().split()
    return list(set(words[:5]))  # Simple topic extraction using first few words


def compare_articles(articles: List[Dict[str, str]]) -> Dict:
    """Analyze topic overlap and coverage differences."""
    topic_data = {idx: extract_topics(article.get("Summary", "")) for idx, article in enumerate(articles)}
    
    common_topics = list(set(itertools.chain(*topic_data.values())))
    coverage_differences = []
    
    for (idx1, topics1), (idx2, topics2) in itertools.combinations(topic_data.items(), 2):
        unique_1 = set(topics1) - set(topics2)
        unique_2 = set(topics2) - set(topics1)
        comparison = f"Article {idx1+1} focuses on {', '.join(unique_1) or 'general news'}, whereas Article {idx2+1} discusses {', '.join(unique_2) or 'general news'}."
        impact = "These differences highlight varying perspectives on the topic."
        coverage_differences.append({"Comparison": comparison, "Impact": impact})
    
    return {"Coverage Differences": coverage_differences, "Topic Overlap": {"Common Topics": common_topics}}


def process_articles(articles: List[Dict[str, str]]) -> Dict:
    """Process a list of articles and add sentiment analysis."""
    analyzer = SentimentAnalyzer()
    sentiment_counts = Counter()
    
    for article in articles:
        print(f"\nAnalyzing sentiment for: {article['Title'][:100]}...")
        sentiment = analyzer.analyze_article(article)
        article["Sentiment"] = sentiment
        sentiment_counts[sentiment["label"]] += 1
        print(f"\u2713 Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})")
    
    topic_comparison = compare_articles(articles)
    
    # Determine final sentiment trend
    if sentiment_counts["POSITIVE"] > sentiment_counts["NEGATIVE"]:
        final_sentiment = "positive"
    elif sentiment_counts["NEGATIVE"] > sentiment_counts["POSITIVE"]:
        final_sentiment = "negative"
    else:
        final_sentiment = "neutral"
    
    comparative_sentiment = {
        "Sentiment Distribution": dict(sentiment_counts),
        **topic_comparison,
        "Final Sentiment Analysis": f"Overall sentiment leans towards {final_sentiment}.",
        "Audio": "/play/hindi_audio"
    }
    
    return {"articles": articles, "comparative_sentiment": comparative_sentiment}