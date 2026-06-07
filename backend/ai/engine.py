import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Initialize the model as a module-level singleton.
# This ensures it is loaded into memory only once per Celery worker process.
MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'

try:
    logger.info(f"Loading native Transformer model: {MODEL_NAME}...")
    _encoder = SentenceTransformer(MODEL_NAME)
    logger.info("Transformer model loaded and warmed up.")
except Exception as e:
    logger.critical(f"Failed to load the embedding engine: {e}")
    raise RuntimeError("AI Triage Engine failed to initialize.") from e

def encode_text(text: str) -> list[float]:
    """
    Converts a raw UTF-8 string into a 768-d embedding vector.
    Returns a native Python list of floats for compatibility with pgvector.
    """
    # max_length truncation prevents memory overflow on massive XML payloads
    vector = _encoder.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return vector.tolist()
