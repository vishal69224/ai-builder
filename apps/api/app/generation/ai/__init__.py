"""Optional local AI helpers for generation enrichment."""

from app.generation.ai.tinygpt_client import (
    fetch_tagline,
    files_pass_quality_gate,
    generate_files,
    health,
)

__all__ = ["fetch_tagline", "generate_files", "files_pass_quality_gate", "health"]
