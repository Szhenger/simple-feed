import numpy as np
from typing import List, Dict

# Expose the internal mechanics to the worker fleet
from .engine import encode_text as generate_embedding
from .centroids import get_workspace_centroids

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculates the cosine similarity between two 768-d vectors.
    Returns a float between -1.0 (opposite) and 1.0 (identical).
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return float(dot_product / (norm_a * norm_b))

def evaluate_threshold(score: float, threshold: float = 0.72) -> bool:
    """
    Evaluates if the similarity score breaches the Closed-World Assumption threshold.
    """
    return score >= threshold
