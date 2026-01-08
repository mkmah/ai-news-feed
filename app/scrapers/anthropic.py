from typing import List
import asyncio
import aiohttp
from html_to_markdown import convert
from app.scrapers.base import Article, BaseScraper


class AnthropicArticle(Article):
    pass


class AnthropicScraper(BaseScraper):
    @property
    def rss_urls(self) -> List[str]:
        return [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        ]

    async def get_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        articles = await super().get_articles(hours)
        return [AnthropicArticle(**article.model_dump()) for article in articles]

    async def url_to_markdown(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
                ) as response:
                    response.raise_for_status()
                    html = await response.text()
                    markdown = convert(html)
                    return markdown
        except Exception:
            return None


if __name__ == "__main__":
    import asyncio

    async def main():
        anthropic = AnthropicScraper()
        articles = await anthropic.get_articles(hours=500)
        print(len(articles))
        if articles:
            # Test async url_to_markdown
            markdown = await anthropic.url_to_markdown(articles[1].url)
            print(markdown[:500] + "..." if markdown else "None")

    asyncio.run(main())
