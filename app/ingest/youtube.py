import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import feedparser
from bs4 import BeautifulSoup
from time import mktime

logger = logging.getLogger(__name__)


class YouTubeIngester:
    """Ingests videos from YouTube channel RSS feeds."""

    def __init__(self, channel_ids: List[str], max_items: int = 5):
        self.channel_ids = channel_ids
        self.max_items = max_items

    def get_feed_url(self, channel_id: str) -> str:
        """Constructs YouTube RSS Feed URL for a channel ID."""
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def parse_published_date(self, entry: Any) -> Optional[datetime]:
        """Parses feedparser entry date tuple to datetime object."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        return datetime.utcnow()

    def fetch_channel(self, channel_id: str) -> List[Dict[str, Any]]:
        """Parses YouTube RSS XML feed for a single channel."""
        items = []
        feed_url = self.get_feed_url(channel_id)
        try:
            logger.info(f"Fetching YouTube feed for channel: {channel_id}")
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get("title", f"YouTube Channel ({channel_id})")

            for entry in feed.entries[: self.max_items]:
                title = entry.get("title", "Untitled Video")
                link = entry.get("link", "")
                if not link:
                    continue

                description = ""
                if "media_description" in entry:
                    description = entry.media_description
                elif "summary" in entry:
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    description = soup.get_text(strip=True)

                pub_date = self.parse_published_date(entry)

                items.append({
                    "title": title,
                    "url": link,
                    "source_type": "youtube",
                    "source_name": source_name,
                    "published_at": pub_date,
                    "raw_content": f"Video Description: {description[:2000]}",
                })
        except Exception as e:
            logger.error(f"Error fetching YouTube channel {channel_id}: {e}")

        return items

    def fetch_all(self) -> List[Dict[str, Any]]:
        """Fetches video items from all configured YouTube channels."""
        all_items = []
        for cid in self.channel_ids:
            items = self.fetch_channel(cid)
            all_items.extend(items)
        return all_items
