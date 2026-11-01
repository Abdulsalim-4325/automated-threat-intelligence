import math
from datetime import datetime, timezone

def calculate_time_decay_confidence(
    base_confidence: int,
    last_seen: datetime,
    source_count: int,
    decay_lambda: float = 0.05
) -> int:
    """
    Computes an indicator's confidence score using exponential time decay
    and a multi-source corroboration bonus.
    
    Formula: Score = min(100, (BaseConfidence + CorroborationBonus) * e^(-lambda * delta_days))
    """
    # Ensure timezone-aware datetime comparison
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    delta_days = max(0.0, (now - last_seen).total_seconds() / 86400.0)

    # Multi-source corroboration bonus (+15 points per extra source beyond the first)
    corroboration_bonus = max(0, (source_count - 1) * 15)
    adjusted_base = min(100, base_confidence + corroboration_bonus)

    # Apply exponential decay: S = S_0 * e^(-lambda * t)
    decayed_score = adjusted_base * math.exp(-decay_lambda * delta_days)

    # Clamp score between 1 and 100
    return max(1, min(100, round(decayed_score)))