"""Ingestion module for fetching news items from blogs and YouTube."""

from app.ingest.blogs import BlogIngester
from app.ingest.youtube import YouTubeIngester

__all__ = ["BlogIngester", "YouTubeIngester"]
