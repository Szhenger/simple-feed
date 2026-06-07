from typing import Dict, List
from feed.models import FeedItem
from .engine import encode_text

# The deterministic seeds that define our Closed-World Assumption.
_AXIOM_SEEDS = {
    FeedItem.AxiomChoices.EDUCATION: (
        "Academic publications, compiler design, algorithms, computer science research, "
        "structural engineering skills, technical learning, and software architecture."
    ),
    FeedItem.AxiomChoices.CAREER: (
        "Engineering leadership, organizational scaling, team management, industry movements, "
        "system design patterns, and professional advancement strategies."
    ),
    FeedItem.AxiomChoices.FINANCE: (
        "Quantitative macroeconomics, market optimization, personal capital allocation, "
        "tax planning, investment strategies, and portfolio management."
    ),
    FeedItem.AxiomChoices.LIFE: (
        "Long-term deterministic tracking, healthcare management, risk mitigation, "
        "fitness, longevity, and collaborative execution frameworks."
    )
}

# Cache the baseline centroids in memory so we don't recalculate the seed text
_BASELINE_CENTROIDS: Dict[str, List[float]] = {}

def _get_baseline_centroids() -> Dict[str, List[float]]:
    """Generates or retrieves the cached 768-d baseline representations."""
    global _BASELINE_CENTROIDS
    if not _BASELINE_CENTROIDS:
        for axiom, text in _AXIOM_SEEDS.items():
            _BASELINE_CENTROIDS[axiom] = encode_text(text)
    return _BASELINE_CENTROIDS

def get_workspace_centroids(workspace_id: str) -> Dict[str, List[float]]:
    """
    Retrieves the centroids for a specific workspace.
    Future Enhancement: Query PostgreSQL for dynamic, user-specific vectors 
    averaged from their explicitly saved FeedItems.
    """
    # For phase 1, we rely on the mathematically verified baselines.
    return _get_baseline_centroids()
