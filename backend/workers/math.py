from datetime import timedelta
from django.utils import timezone

def calculate_next_poll_time(base_interval: int, max_interval: int, consecutive_misses: int) -> timezone.datetime:
    """
    Calculates the next polling timestamp using exponential backoff.
    Formula: ΔT_next = min(T_max, T_base * γ^n)
    Where γ (gamma) = 1.5 and n = consecutive_misses.
    """
    gamma = 1.5
    
    # Calculate the decay multiplier
    decay_multiplier = base_interval * (gamma ** consecutive_misses)
    
    # Enforce the upper bound (T_max)
    delta_minutes = min(max_interval, int(decay_multiplier))
    
    return timezone.now() + timedelta(minutes=delta_minutes)
