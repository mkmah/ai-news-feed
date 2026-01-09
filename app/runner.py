import asyncio
import logging
from datetime import datetime
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
from app.services.process_anthropic import process_anthropic_articles
from app.services.process_youtube import process_youtube_transcripts
from app.services.process_digest import process_digests
from app.services.process_email import send_digest_email

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Feeds(BaseModel):
    youtube: List[YoutubeVideo]
    openai: List[OpenAIArticle]
    anthropic: List[AnthropicArticle]


async def run_scrapers(hours: int = 24):
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


async def run_daily_pipeline(hours: int = 24, top_n: int = 10) -> dict:
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Starting Daily AI News Aggregator Pipeline")
    logger.info("=" * 60)
    
    results = {
        "start_time": start_time.isoformat(),
        "scraping": {},
        "processing": {},
        "digests": {},
        "email": {},
        "success": False
    }
    
    try:
        logger.info("\n[1/5] Scraping articles from sources...")
        scraping_results = await run_scrapers(hours=hours)
        results["scraping"] = {
            "youtube": len(scraping_results.youtube),
            "openai": len(scraping_results.openai),
            "anthropic": len(scraping_results.anthropic)
        }
        logger.info(f"✓ Scraped {results['scraping']['youtube']} YouTube videos, "
                    f"{results['scraping']['openai']} OpenAI articles, "
                    f"{results['scraping']['anthropic']} Anthropic articles")
        
        logger.info("\n[2/5] Processing Anthropic markdown...")
        anthropic_result = await process_anthropic_articles()
        results["processing"]["anthropic"] = anthropic_result
        logger.info(f"✓ Processed {anthropic_result['processed']} Anthropic articles "
                    f"({anthropic_result['failed']} failed)")
        
        logger.info("\n[3/5] Processing YouTube transcripts...")
        youtube_result = await process_youtube_transcripts()
        results["processing"]["youtube"] = youtube_result
        logger.info(f"✓ Processed {youtube_result['processed']} transcripts "
                    f"({youtube_result['unavailable']} unavailable)")
        
        logger.info("\n[4/5] Creating digests for articles...")
        digest_result = await process_digests()
        results["digests"] = digest_result
        logger.info(f"✓ Created {digest_result['processed']} digests "
                    f"({digest_result['failed']} failed out of {digest_result['total']} total)")
        
        logger.info("\n[5/5] Generating and sending email digest...")
        email_result = await send_digest_email(hours=hours, top_n=top_n)
        results["email"] = email_result
        
        if email_result["success"]:
            logger.info(f"✓ Email sent successfully with {email_result['articles_count']} articles")
            results["success"] = True
        else:
            logger.error(f"✗ Failed to send email: {email_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        results["error"] = str(e)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = duration
    
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Scraped: {results['scraping']}")
    logger.info(f"Processed: {results['processing']}")
    logger.info(f"Digests: {results['digests']}")
    logger.info(f"Email: {'Sent' if results['success'] else 'Failed'}")
    logger.info("=" * 60)
    
    return results


if __name__ == "__main__":
    async def main():
        result = await run_daily_pipeline(hours=24, top_n=10)
        exit(0 if result["success"] else 1)
    
    asyncio.run(main())
