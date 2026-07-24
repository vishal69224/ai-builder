"""Intent helpers — negation-aware keyword matching for niche routing."""

from __future__ import annotations

import re

FOOTWEAR_TERMS = (
    "shoe",
    "shoes",
    "sneaker",
    "sneakers",
    "footwear",
    "loafer",
    "loafers",
    "boot",
    "boots",
    "sandal",
    "sandals",
    "running shoes",
    "football shoes",
    "athletic shoes",
)

CLOTHING_TERMS = (
    "clothing",
    "apparel",
    "fashion",
    "boutique",
    "garment",
    "streetwear",
    "menswear",
    "womenswear",
    "hoodie",
    "hoodies",
    "t-shirt",
    "t-shirts",
    "dress",
    "dresses",
    "blazer",
    "jeans",
    "knitwear",
    "co-ord",
    "coord",
)

# Phrases that mean the user wants clothing, not shoes
STRONG_CLOTHING = (
    "clothing brand",
    "fashion clothing",
    "fashion brand",
    "clothing store",
    "apparel brand",
    "exclusively sell clothing",
    "sell clothing",
    "luxury fashion",
    "premium fashion",
    "editorial fashion",
    "clothing and fashion",
    "fashion accessories",
)

# User is explicitly forbidding footwear
FORBID_FOOTWEAR = (
    "do not generate a shoe",
    "don't generate a shoe",
    "do not generate shoe",
    "not a shoe store",
    "never appear",
    "shoes should never",
    "do not use sneaker",
    "do not use shoe",
    "don't use sneaker",
    "avoid:\n- shoes",
    "avoid:\n- sneakers",
    "avoid shoes",
    "avoid sneakers",
    "no shoes",
    "no sneakers",
    "without shoes",
    "not shoes",
    "shoe store",  # often appears as "Do NOT generate a shoe store"
)


def sanitize_prompt_for_matching(prompt: str) -> str:
    """Remove Avoid / Do NOT / IMPORTANT negation blocks so forbidden words don't classify the niche."""
    text = prompt or ""
    # Cut common exclusion sections
    patterns = [
        r"(?is)\bimportant\s*:.*?(?=\n\s*\n|target audience|brand style|color palette|typography|create the following|homepage|products should|features\s*:|design inspiration|image style|$)",
        r"(?is)\bavoid\s*:.*?(?=\n\s*\n|target audience|brand style|the final result|features\s*:|design inspiration|$)",
        r"(?is)\bdo not\b.*?(?=\n\s*\n|target audience|brand style|create the following|products should|$)",
        r"(?is)\bdon'?t\b.*?(?=\n\s*\n|target audience|brand style|$)",
    ]
    cleaned = text
    for pat in patterns:
        cleaned = re.sub(pat, " ", cleaned)
    # Remove inline "Do NOT …" sentences
    cleaned = re.sub(r"(?i)\bdo not\b[^.!\n]*[.!]?", " ", cleaned)
    cleaned = re.sub(r"(?i)\bdon'?t\b[^.!\n]*[.!]?", " ", cleaned)
    cleaned = re.sub(r"(?i)\bnever\b[^.!\n]*[.!]?", " ", cleaned)
    cleaned = re.sub(r"(?i)\bshoes should never\b[^.!\n]*[.!]?", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    # Common typos so casual prompts still match niches
    typo_map = {
        "ganerator": "generator",
        "generater": "generator",
        "attarctive": "attractive",
        "atractive": "attractive",
        "websit": "website",
        "protfolio": "portfolio",
        "portfoilo": "portfolio",
    }
    for bad, good in typo_map.items():
        cleaned = cleaned.replace(bad, good)
    return cleaned


def explicitly_forbids_footwear(prompt: str) -> bool:
    lowered = (prompt or "").lower()
    if any(p in lowered for p in FORBID_FOOTWEAR):
        # "do not generate a shoe store" / avoid shoes
        if re.search(r"(?i)do not|don'?t|avoid|never|exclusively sell clothing|not a shoe", lowered):
            return True
    if re.search(r"(?i)do not use (sneakers|shoes|boots|sandals|footwear)", lowered):
        return True
    if re.search(r"(?i)avoid[\s\S]{0,400}\b(shoes|sneakers|boots)\b", lowered):
        return True
    return False


def has_strong_clothing_intent(prompt: str) -> bool:
    lowered = (prompt or "").lower()
    if any(p in lowered for p in STRONG_CLOTHING):
        return True
    # Pages Men + Women + clothing products is a strong signal
    if ("men" in lowered and "women" in lowered) and any(
        t in lowered for t in ("clothing", "fashion", "hoodie", "dress", "blazer", "t-shirt")
    ):
        return True
    return False


def positive_footwear_intent(prompt: str) -> bool:
    """True only if footwear is requested outside negation / avoid blocks."""
    if explicitly_forbids_footwear(prompt) and has_strong_clothing_intent(prompt):
        return False
    cleaned = sanitize_prompt_for_matching(prompt)
    if explicitly_forbids_footwear(prompt) and not any(
        t in cleaned for t in ("shoe store", "sneaker store", "footwear store", "buy shoes")
    ):
        # Forbidden + no positive shoe shop ask
        if has_strong_clothing_intent(prompt):
            return False
    return any(re.search(rf"\b{re.escape(t)}\b", cleaned) for t in FOOTWEAR_TERMS)


def positive_clothing_intent(prompt: str) -> bool:
    if has_strong_clothing_intent(prompt):
        return True
    cleaned = sanitize_prompt_for_matching(prompt)
    return any(re.search(rf"\b{re.escape(t)}\b", cleaned) for t in CLOTHING_TERMS)
