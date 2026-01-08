import asyncio
from app.db.repo import Repository
from app.db.connection import get_session
from app.scrapers.anthropic import AnthropicScraper


async def process_anthropic_articles():
    scraper = AnthropicScraper()

    processed = 0
    failed = 0
    articles = []

    async with get_session() as session:
        repo = Repository(session=session)
        articles = await repo.get_anthropic_articles_without_markdown()
        for article in articles:
            markdown = await scraper.url_to_markdown(article.url)
            try:
                if markdown:
                    if not await repo.update_anthropic_article_markdown(
                        article.guid, markdown
                    ):
                        raise Exception("Failed to update article markdown")
                    processed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"Error processing article {article.guid}: {e}")
                continue

    return {"total": len(articles), "processed": processed, "failed": failed}


if __name__ == "__main__":

    async def main():
        result = await process_anthropic_articles()
        print(f"Total articles: {result['total']}")
        print(f"Processed: {result['processed']}")
        print(f"Failed: {result['failed']}")

    asyncio.run(main())
