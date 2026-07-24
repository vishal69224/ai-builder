"""Optional AI Planner (Phase 7) — enrich WebsitePlan via OpenAI-compatible JSON.

Never writes React files. Falls back to the rules WebsitePlanner on any failure.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings
from app.generation.pipeline import PromptAnalysis, WebsitePlan
from app.generation.planner.niches import NICHES

logger = logging.getLogger("ai_planner")


class AIPlanner:
    def maybe_enrich(
        self,
        analysis: PromptAnalysis,
        website_plan: WebsitePlan,
    ) -> WebsitePlan:
        settings = get_settings()
        if not settings.gen_v2_ai_planner:
            return website_plan
        if settings.ai_mock or not settings.ai_api_key:
            return website_plan

        try:
            import httpx

            system = (
                "You are a website planning assistant. Return ONLY valid JSON with keys: "
                "niche (one of the allowed niche ids), brand_name, tagline, hero_headline, "
                "product_types (array), forbidden_products (array). "
                f"Allowed niches: {', '.join(sorted(NICHES.keys()))}."
            )
            user = (
                f"Prompt: {analysis.raw_prompt}\n"
                f"Current plan niche: {website_plan.niche}\n"
                f"Current brand: {website_plan.brand_name}\n"
            )
            resp = httpx.post(
                f"{settings.ai_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.ai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.ai_model,
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                timeout=12.0,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(raw)
            return self._merge(website_plan, data)
        except Exception as exc:
            logger.info("AI planner skipped: %s", exc)
            return website_plan

    def _merge(self, plan: WebsitePlan, data: dict[str, Any]) -> WebsitePlan:
        niche_id = str(data.get("niche") or plan.niche)
        if niche_id not in NICHES:
            niche_id = plan.niche
        # Rebuild from rules planner with same analysis fields but override brand/tagline via niche
        # Keep structure; patch fields
        brand = str(data.get("brand_name") or plan.brand_name).strip() or plan.brand_name
        tagline = str(data.get("tagline") or plan.tagline).strip() or plan.tagline
        products = data.get("product_types")
        forbidden = data.get("forbidden_products")
        if not isinstance(products, list):
            products = plan.product_types
        if not isinstance(forbidden, list):
            forbidden = plan.forbidden_products

        # If AI changed niche, rebuild plan from niche defaults using WebsitePlanner path
        if niche_id != plan.niche:
            # Keep original plan pages but swap niche metadata
            niche = NICHES[niche_id]
            plan.niche = niche_id
            plan.product_types = list(niche.product_types)
            plan.forbidden_products = list(niche.forbidden_products)
            plan.image_collections = list(niche.image_collections)
            plan.theme = {**plan.theme, "token_preset": niche.token_preset, "style": niche.design_style}
            plan.hero = {"variant": niche.hero_variant}
            plan.navbar = {**plan.navbar, "variant": niche.navbar_variant}
            plan.footer = {"variant": niche.footer_variant}

        plan.brand_name = brand
        plan.tagline = tagline
        plan.product_types = [str(p) for p in products][:12]
        plan.forbidden_products = [str(p) for p in forbidden][:12]
        if isinstance(plan.intent, dict):
            plan.intent["business_name"] = brand
            plan.intent["product_types"] = plan.product_types
            plan.intent["forbidden_products"] = plan.forbidden_products
            plan.seo = {**plan.seo, "tagline": tagline}
        return plan
