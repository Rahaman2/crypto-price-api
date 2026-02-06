from fastapi import APIRouter, Query
from typing import Optional
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime

router = APIRouter()

# Free RSS feeds for crypto news
RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
    "bitcoinmagazine": "https://bitcoinmagazine.com/feed",
    "decrypt": "https://decrypt.co/feed",
}


async def fetch_rss_feed(url: str, source: str, limit: int = 10):
    """Fetch and parse RSS feed."""
    articles = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                root = ET.fromstring(response.content)

                # Handle both RSS 2.0 and Atom feeds
                items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for item in items[:limit]:
                    # RSS 2.0 format
                    title = item.find("title")
                    link = item.find("link")
                    pub_date = item.find("pubDate")
                    description = item.find("description")

                    # Atom format fallback
                    if title is None:
                        title = item.find("{http://www.w3.org/2005/Atom}title")
                    if link is None:
                        link_elem = item.find("{http://www.w3.org/2005/Atom}link")
                        link_text = link_elem.get("href") if link_elem is not None else None
                    else:
                        link_text = link.text

                    articles.append({
                        "title": title.text if title is not None else None,
                        "url": link_text if isinstance(link_text, str) else (link.text if link is not None else None),
                        "published": pub_date.text if pub_date is not None else None,
                        "description": description.text[:200] + "..." if description is not None and description.text else None,
                        "source": source,
                    })
    except Exception as e:
        pass  # Skip failed feeds silently

    return articles


@router.get("")
async def get_crypto_news(
    limit: int = Query(default=20, ge=1, le=50, description="Number of articles per source"),
    source: Optional[str] = Query(default=None, description="Filter by source: coindesk, cointelegraph, bitcoinmagazine, decrypt"),
):
    """
    Get latest cryptocurrency news from multiple free sources.

    - **limit**: Number of articles to return per source (1-50)
    - **source**: Optional filter for specific news source
    """
    all_articles = []

    if source and source.lower() in RSS_FEEDS:
        # Fetch from specific source
        feeds_to_fetch = {source.lower(): RSS_FEEDS[source.lower()]}
    else:
        # Fetch from all sources
        feeds_to_fetch = RSS_FEEDS

    for src_name, url in feeds_to_fetch.items():
        articles = await fetch_rss_feed(url, src_name, limit)
        all_articles.extend(articles)

    # Sort by published date if available
    all_articles.sort(
        key=lambda x: x.get("published") or "",
        reverse=True
    )

    return {
        "count": len(all_articles),
        "sources": list(feeds_to_fetch.keys()),
        "articles": all_articles[:limit * len(feeds_to_fetch)] if not source else all_articles,
    }


@router.get("/sources")
async def get_news_sources():
    """Get list of available news sources."""
    return {
        "sources": list(RSS_FEEDS.keys()),
        "description": "Use ?source=<name> to filter news by source"
    }
