"""Train a local website-type classifier from the type catalog (no API key)."""

from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.generation.analyzer.website_types import WEBSITE_TYPES, catalog_stats

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "website_classifier.joblib"
META_PATH = ARTIFACT_DIR / "model_meta.json"

# Templates used to synthesize training prompts from catalog keywords
TEMPLATES = [
    "Build a {label} website",
    "Create a modern {label} with {kw}",
    "I need a {kw} website for my business",
    "Design a {label} landing page with {kw}",
    "Make a responsive {label} site",
    "{label} website with dark mode and animations",
    "Professional {kw} web app using React and Tailwind",
    "Generate a {label} for {kw}",
]


def _synthetic_samples(max_per_type: int = 12) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []
    rng = random.Random(42)

    for wt in WEBSITE_TYPES:
        kws = list(wt.keywords[:6]) or [wt.label.lower()]
        samples = set()
        for tpl in TEMPLATES:
            kw = rng.choice(kws)
            samples.add(tpl.format(label=wt.label, kw=kw))
        for kw in kws:
            samples.add(f"Build a {kw} website")
            samples.add(f"Modern {kw} site with Tailwind CSS")
        for s in list(samples)[:max_per_type]:
            texts.append(s)
            labels.append(wt.id)

    return texts, labels


def train_and_save() -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    texts, labels = _synthetic_samples()

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=50000)),
            ("clf", LogisticRegression(max_iter=2000, solver="lbfgs")),
        ]
    )
    pipeline.fit(texts, labels)

    joblib.dump({"pipeline": pipeline, "type_ids": sorted(set(labels))}, MODEL_PATH)

    meta = {
        "model": "tfidf_logistic_website_classifier",
        "version": "1.0.0",
        "training_samples": len(texts),
        "website_types": len(set(labels)),
        "catalog": catalog_stats(),
        "requires_api_key": False,
    }
    META_PATH.write_text(json.dumps(meta, indent=2))

    # Quick holdout sanity check
    test_prompts = [
        ("Build a modern coffee shop website", "coffee"),
        ("Create a travel agency website", "travel"),
        ("Portfolio for a photographer", "portfolio"),
    ]
    checks = []
    for prompt, hint in test_prompts:
        pred_id = pipeline.predict([prompt])[0]
        checks.append({"prompt": prompt, "predicted_id": pred_id, "hint": hint})

    meta["sanity_checks"] = checks
    META_PATH.write_text(json.dumps(meta, indent=2))
    return meta


def load_model() -> Pipeline | None:
    if not MODEL_PATH.exists():
        return None
    data = joblib.load(MODEL_PATH)
    return data["pipeline"]
