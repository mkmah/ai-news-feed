import asyncio
from typing import Optional
from app.agent.digest import DigestAgent
from app.db.repo import Repository
from app.db.connection import get_session
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def process_digests(limit: Optional[int] = None) -> dict:
    agent = DigestAgent()

    processed = 0
    failed = 0
    total = 0

    async with get_session() as session:
        repo = Repository(session=session)
        articles = await repo.get_articles_without_digest(limit=limit)
        total = len(articles)

        logger.info(f"Starting digest processing for {total} articles")

        for idx, article in enumerate(articles, 1):
            article_type = article["type"]
            article_id = article["id"]
            article_title = (
                article["title"][:60] + "..."
                if len(article["title"]) > 60
                else article["title"]
            )

            logger.info(
                f"[{idx}/{total}] Processing {article_type}: {article_title} (ID: {article_id})"
            )

            try:
                digest_result = await agent.generate_digest(
                    title=article["title"],
                    content=article["content"],
                    article_type=article_type,
                )

                if digest_result:
                    await repo.create_digest(
                        article_type=article_type,
                        article_id=article_id,
                        url=article["url"],
                        title=digest_result.title,
                        summary=digest_result.summary,
                    )
                    processed += 1
                    logger.info(
                        f"✓ Successfully created digest for {article_type} {article_id}"
                    )
                else:
                    failed += 1
                    logger.warning(
                        f"✗ Failed to generate digest for {article_type} {article_id}"
                    )
            except Exception as e:
                failed += 1
                logger.error(f"✗ Error processing {article_type} {article_id}: {e}")

    logger.info(
        f"Processing complete: {processed} processed, {failed} failed out of {total} total"
    )

    return {"total": total, "processed": processed, "failed": failed}


if __name__ == "__main__":

    async def main():
        result = await process_digests()
        print(f"Total articles: {result['total']}")
        print(f"Processed: {result['processed']}")
        print(f"Failed: {result['failed']}")

    asyncio.run(main())
