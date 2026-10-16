import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import feedparser
from bs4 import BeautifulSoup
from time import mktime

logger = logging.getLogger(__name__)


class BlogIngester:
    """Ingests articles from RSS/Atom blog feeds."""

    def __init__(self, feed_urls: List[str], max_items: int = 5):
        self.feed_urls = feed_urls
        self.max_items = max_items

    def clean_html(self, raw_html: str) -> str:
        """Strips HTML tags and extracts clean text."""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def parse_published_date(self, entry: Any) -> Optional[datetime]:
        """Parses feedparser entry date tuple to datetime object."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime.fromtimestamp(mktime(entry.updated_parsed))
        return datetime.utcnow()

    def fetch_feed(self, url: str) -> List[Dict[str, Any]]:
        """Parses a single RSS feed URL and extracts structured article dictionaries."""
        items = []
        try:
            logger.info(f"Fetching RSS feed: {url}")
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url.split("/")[2] if "//" in url else url)

            for entry in feed.entries[: self.max_items]:
                title = entry.get("title", "Untitled")
                link = entry.get("link", "")
                if not link:
                    continue

                raw_body = ""
                if "content" in entry and len(entry.content) > 0:
                    raw_body = entry.content[0].get("value", "")
                elif "summary" in entry:
                    raw_body = entry.get("summary", "")

                clean_text = self.clean_html(raw_body)
                pub_date = self.parse_published_date(entry)

                items.append({
                    "title": title,
                    "url": link,
                    "source_type": "blog",
                    "source_name": source_name,
                    "published_at": pub_date,
                    "raw_content": clean_text[:4000],
                })
        except Exception as e:
            logger.error(f"Error fetching blog feed {url}: {e}")

        return items

    def fetch_all(self) -> List[Dict[str, Any]]:
        """Fetches items from all configured blog RSS feeds."""
        all_items = []
        for url in self.feed_urls:
            items = self.fetch_feed(url)
            all_items.extend(items)
        return all_items
