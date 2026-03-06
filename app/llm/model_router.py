"""Reading-type to model mapping for multi-model cost optimization."""
from __future__ import annotations

from app.config import settings

# Premium tier: complex, high-quality interpretation required
_PREMIUM_TYPES: frozenset[str] = frozenset({
    "saju_reading",
    "compatibility",
    "celebrity_compatibility",
    "situation_career_change",
})

# Standard tier: everything else uses Haiku
_HAIKU_MODEL = "claude-haiku-4-5-20251001"


def get_model_for_type(reading_type: str) -> str:
    """Return the appropriate model ID for the given reading type.

    Premium types use the configured default model (Sonnet).
    All other types use Haiku for cost optimization.
    """
    if reading_type in _PREMIUM_TYPES:
        return settings.llm_model
    return _HAIKU_MODEL
