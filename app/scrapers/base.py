import asyncio
import feedparser
from datetime import timedelta
from datetime import timezone
from typing import List
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Article(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None


class BaseScraper(ABC):
    @property
    @abstractmethod
    def rss_urls(self) -> List[str]:
        pass

    async def get_articles(self, hours: int = 24) -> List[Article]:
        now = datetime.now(timezone.utc)
        cut_off_time = now - timedelta(hours=hours)
        articles: List[Article] = []
        seen_guids = set()

        for rss_url in self.rss_urls:
            feed = await asyncio.to_thread(feedparser.parse, rss_url)
            if not feed.entries:
                continue

            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue

                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published_time < cut_off_time:
                    continue

                guid = entry.get("id", entry.get("link", ""))
                if guid in seen_guids:
                    continue

                seen_guids.add(guid)
                articles.append(
                    Article(
                        title=entry.get("title", ""),
                        description=entry.get("description", ""),
                        url=entry.get("link", ""),
                        guid=guid,
                        published_at=published_time,
                        category=entry.get("tags", [{}])[0].get("term")
                        if entry.get("tags")
                        else None,
                    )
                )

        return articles
