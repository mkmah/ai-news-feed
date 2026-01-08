import asyncio
from typing import List
from pydantic import BaseModel

from app.db.repo import Repository
from app.db.connection import get_session

from app.scrapers import (
    YoutubeScraper,
    OpenAIScraper,
    AnthropicScraper,
    YoutubeVideo,
    OpenAIArticle,
    AnthropicArticle,
)
from app.settings import settings


class Feeds(BaseModel):
    youtube: List[YoutubeVideo]
    openai: List[OpenAIArticle]
    anthropic: List[AnthropicArticle]


async def run_scrappers(hours: int = 24):
    youtube_scraper = YoutubeScraper()
    openai_scraper = OpenAIScraper()
    anthropic_scraper = AnthropicScraper()

    youtube_videos: List[YoutubeVideo] = []
    for channel_id in settings.youtube_channels:
        videos = await youtube_scraper.get_latest_videos(channel_id, hours=hours)
        youtube_videos.extend(videos)

    openai_articles: List[OpenAIArticle] = await openai_scraper.get_articles(
        hours=hours
    )

    anthropic_articles: List[AnthropicArticle] = await anthropic_scraper.get_articles(
        hours=hours
    )

    async with get_session() as session:
        repo = Repository(session=session)
        await repo.bulk_create_youtube_videos(youtube_videos)
        await repo.bulk_create_openai_articles(openai_articles)
        await repo.bulk_create_anthropic_articles(anthropic_articles)

    return Feeds(
        youtube=youtube_videos,
        openai=openai_articles,
        anthropic=anthropic_articles,
    )


async def main(hours: int = 24):
    results = await run_scrappers(hours=hours)

    print(f"\n=== Scraping Results (last {hours} hours) ===")
    print(f"YouTube videos: {len(results.youtube)}")
    print(f"OpenAI articles: {len(results.openai)}")
    print(f"Anthropic articles: {len(results.anthropic)}")

    return results


if __name__ == "__main__":
    import sys

    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    asyncio.run(main(hours=hours))
