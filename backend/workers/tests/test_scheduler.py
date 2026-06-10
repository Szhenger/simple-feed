import pytest
from datetime import timedelta
from workers.scheduler import calculate_next_poll, MAX_POLL_INTERVAL_MINUTES

class TestExponentialBackoffOrchestration:

    def test_backoff_clamps_at_maximum_threshold(self):
        """
        If a feed has been dead for years, the N_misses multiplier could theoretically 
        overflow PostgreSQL's integer field. We must verify the hard ceiling.
        """
        base_interval = 60 # 1 hour
        massive_misses = 50 # 2^50 would overflow standard minute counters
        
        next_poll_minutes = calculate_next_poll(base_interval, massive_misses)
        
        # Verify the math clamped strictly to our safety constant (e.g., 1 week)
        assert next_poll_minutes == MAX_POLL_INTERVAL_MINUTES

    def test_successful_poll_resets_decay_instantly(self):
        """
        If a feed suddenly publishes after a long silence, the orchestrator 
        must instantly snap the polling window back to the aggressive baseline.
        """
        base_interval = 15
        misses = 0 # Simulating a successful poll resetting the counter
        
        next_poll_minutes = calculate_next_poll(base_interval, misses)
        
        # 15 * 2^0 = 15
        assert next_poll_minutes == 15
