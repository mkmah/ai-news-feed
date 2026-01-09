from typing import Optional
from pydantic import BaseModel
from openai import AsyncOpenAI, DefaultAioHttpClient

from app.settings import settings


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """You are an expert AI Technical Analyst. Your goal is to synthesize complex inputs (research papers, technical blogs, video transcripts) into high-signal executive digests for a technical audience.

Output Format:
1. TITLE: A punchy, objectively phrased headline (5-10 words).
2. SUMMARY: A concise 2-3 sentence paragraph capturing the core innovation or news.
3. SIGNIFICANCE: A single sentence explaining the "So What?" — why this matters to the industry.

Guidelines:
- Tone: Professional, objective, and authoritative.
- Terminology: Use correct technical jargon (e.g., "transformer architecture" not "computer brain").
- Source Material: If the input is a transcript, ignore conversational filler. If a paper, focus on the methodology and results.

Negative Constraints:
- Do not use clickbait or hype words (e.g., "Game-changer," "Revolutionary," "Mind-blowing").
- Do not start the summary with meta-phrases like "This article discusses..." or "The video explains..." -> Jump straight into the facts.
- Do not include hashtags or emojis."""


class DigestAgent:
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.system_prompt = PROMPT
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            http_client=DefaultAioHttpClient(),
        )

    async def generate_digest(
        self, title: str, content: str, article_type: str
    ) -> Optional[DigestOutput]:
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

            response = await self.client.responses.create(
                model=self.model,
                instructions=self.system_prompt,
                temperature=0.7,
                input=user_prompt,
                text_format=DigestOutput,
            )

            return response.output_parsed
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None
