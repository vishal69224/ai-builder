"""PromptAgent — owns prompt understanding only (Phase 4).

Collaborators remain at their existing module paths; this agent is the sole
runtime owner of the analyze → enrich → extract sequence.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
from app.generation.context import GenerationContext
from app.generation.extractor.requirements import RequirementExtractor


class PromptAgent:
    """Analyze prompt and extract structured requirements into GenerationContext."""

    def __init__(
        self,
        analyzer: PromptAnalyzer | None = None,
        extractor: RequirementExtractor | None = None,
    ) -> None:
        self.analyzer = analyzer or PromptAnalyzer()
        self.extractor = extractor or RequirementExtractor()

    def execute(self, context: GenerationContext) -> GenerationContext:
        analysis = self.analyzer.analyze(context.prompt)

        # Optional TinyGPT enrichment (localhost) — soft-fail, same as pre-Phase-4 Engine
        try:
            from app.generation.ai.tinygpt_client import fetch_tagline

            tagline = fetch_tagline(context.prompt, base_url=get_settings().tinygpt_base_url)
            if tagline:
                if not isinstance(analysis.seo, dict):
                    analysis.seo = {}
                analysis.seo["tagline"] = tagline
        except Exception:
            pass

        requirements = self.extractor.extract(analysis)
        context.analysis = analysis
        context.requirements = requirements
        return context
