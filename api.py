from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import os

from utils.scraper import fetch_news
from utils.sentiment import process_articles
from utils.tts import generate_hindi_tts
from googletrans import Translator  # Import Translator
app = FastAPI()

# Ensure directories exist
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.get("/news")
async def get_news(company: str = Query(..., description="Company name to fetch news for")):
    """Fetch 10 news articles for a company and analyze sentiment and coverage differences."""
    print(f"Fetching news for {company}...")

    # Fetch and process articles
    articles = fetch_news(company, num_articles=10)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found for this company")
    processed_articles = process_articles(articles)
    
    # Extract required fields for each article
    formatted_articles = [
        {
            "Title": article["Title"],
            "Summary": article.get("Summary", "Summary not available"),
            "Sentiment": article["Sentiment"],
            "Topics": article.get("Topics", [])
        }
        for article in processed_articles["articles"]
    ]
    
    # Analyze sentiment, topic overlap, and coverage differences
    sentiment_analysis = processed_articles["comparative_sentiment"]
    
    # Determine the dominant sentiment
    sentiment_counts = sentiment_analysis["Sentiment Distribution"]
    dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get, default="NEUTRAL")
    final_sentiment_summary_en = f"Overall sentiment leans towards {dominant_sentiment.lower()}."

    # ✅ Translate to Hindi before TTS
    translator = Translator()
    final_sentiment_summary_hi = translator.translate(final_sentiment_summary_en, src="en", dest="hi").text
    
    # ✅ Generate Hindi TTS
    hindi_audio_path = generate_hindi_tts(final_sentiment_summary_hi)

    return {
        "Company": company,
        "Articles": formatted_articles,
        "Coverage Differences": sentiment_analysis["Coverage Differences"],
        "Topic Overlap": sentiment_analysis["Topic Overlap"],
        "Comparative Sentiment Score": sentiment_counts,
        "Final Sentiment Analysis": final_sentiment_summary_hi,  # ✅ Now in Hindi
        "Audio": f"/play/{os.path.basename(hindi_audio_path)}"
    }

@app.get("/play/{filename}")
async def stream_audio(filename: str):
    """Stream the saved audio file."""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return StreamingResponse(open(file_path, "rb"), media_type="audio/mpeg")