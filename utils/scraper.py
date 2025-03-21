import urllib.parse
import feedparser
import re
from collections import Counter

def extract_keywords(text, num_keywords=5):
    """Extract top keywords from text."""
    if not text:
        return []  # Avoid errors if text is None
    
    words = re.findall(r'\b\w{4,}\b', text.lower())  
    common_words = {"the", "and", "with", "from", "this", "that", "said", "will", "have"}
    filtered_words = [word for word in words if word not in common_words]
    
    return [word for word, _ in Counter(filtered_words).most_common(num_keywords)]

def summarize_text(text, max_words=20):
    """Summarize text to a limited number of words."""
    if not text:
        return "Summary not available"
    
    words = text.split()
    return " ".join(words[:max_words]) + ('...' if len(words) > max_words else '')

def fetch_news(company_name, num_articles=10):
    """Fetch top news articles about a company from Bing News RSS feed."""
    
    search_url = f"https://www.bing.com/news/search?q={urllib.parse.quote(company_name)}&format=rss"
    
    try:
        feed = feedparser.parse(search_url)
        if not feed.entries:
            print("No news articles found.")
            return []  # Return empty list if no data

        articles = []
        
        for entry in feed.entries[:num_articles]:  # Limit articles directly
            title = entry.get("title", "No Title")
            description = entry.get("summary", "Summary not available")
            link = entry.get("link", "#")
            published_date = entry.get("published", "Unknown Date")
            
            topics = extract_keywords(description)
            summary = summarize_text(description)
            
            articles.append({
                "Title": title,
                "Summary": summary,
                "Topics": topics,
                "Link": link,
                "Published Date": published_date
            })

        return articles  # No need to slice again
    
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
