from datetime import datetime, timedelta, timezone
from app.normalizer.scoring import calculate_time_decay_confidence

def test_calculate_time_decay_confidence():
    now = datetime.now(timezone.utc)
    
    # 1. Fresh indicator (0 days old), 1 source, base confidence 80 -> should remain 80
    score_fresh = calculate_time_decay_confidence(80, now, 1)
    assert score_fresh == 80
    
    # 2. Corroboration bonus: 2 sources (+15 points) -> 80 + 15 = 95
    score_bonus = calculate_time_decay_confidence(80, now, 2)
    assert score_bonus == 95
    
    # 3. Maximum cap enforcement: 90 base + 2 sources (+15) -> 105 -> capped at 100
    score_capped = calculate_time_decay_confidence(90, now, 2)
    assert score_capped == 100
    
    # 4. Exponential Time Decay: 30 days old, lambda 0.05
    # Math: S = 100 * exp(-0.05 * 30) = 100 * exp(-1.5) ~ 22.3
    old_date = now - timedelta(days=30)
    score_decayed = calculate_time_decay_confidence(100, old_date, 1, decay_lambda=0.05)
    assert 20 <= score_decayed <= 25