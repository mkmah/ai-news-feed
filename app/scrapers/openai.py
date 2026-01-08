from typing import List
from .base import BaseScraper, Article


class OpenAIArticle(Article):
    pass


class OpenAIScraper(BaseScraper):
    @property
    def rss_urls(self) -> List[str]:
        return ["https://openai.com/news/rss.xml"]

    async def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        articles = await super().get_articles(hours)
        return [OpenAIArticle(**article.model_dump()) for article in articles]


if __name__ == "__main__":
    import asyncio

    async def main():
        openai = OpenAIScraper()
        articles = await openai.get_articles(hours=500)
        print(len(articles))

    asyncio.run(main())
