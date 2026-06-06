import httpx
from typing import List, Dict
from django.db import transaction
from django.utils import timezone
from celery.utils.log import get_task_logger

from feed.models import FeedSource, FeedItem
from workers.math import calculate_next_poll_time
from workers.locks import acquire_feed_lock

# Architecture stubs for the decoupled AI and Kernel layers
from ai.triage import generate_embedding, get_workspace_centroids, cosine_similarity
from kernel.client import parse_feed_stream  # C++20 AVX-512 FFI Bridge

logger = get_task_logger(__name__)

SIMILARITY_THRESHOLD = 0.72  # τ >= 0.72

def process_feed_source(source_id: str) -> None:
    """
    The deterministic pipeline for feed parsing and AI triage.
    """
    with acquire_feed_lock(source_id) as acquired:
        if not acquired:
            return  # Lock held by another worker. Silently exit.

        try:
            source = FeedSource.objects.get(id=source_id, is_active=True)
        except FeedSource.DoesNotExist:
            logger.error(f"FeedSource {source_id} not found or inactive.")
            return

        # 1. Network I/O
        try:
            # We use an explicit timeout to prevent worker thread starvation
            response = httpx.get(source.url, timeout=15.0, follow_redirects=True)
            response.raise_for_status()
            raw_xml_bytes = response.content
        except httpx.RequestError as e:
            logger.error(f"Network failure for {source.url}: {e}")
            _update_polling_decay(source, success=False)
            return

        # 2. Kernel Offload (C++20 AVX-512 SIMD Tokenization)
        # Bypasses the Python GIL entirely for string heavy-lifting
        parsed_entries: List[Dict] = parse_feed_stream(raw_xml_bytes)

        if not parsed_entries:
            _update_polling_decay(source, success=False)
            return

        # 3. AI Triage & State Transition (Batch Processing)
        new_items_count = 0
        centroids = get_workspace_centroids(source.workspace_id)

        with transaction.atomic():
            for entry in parsed_entries:
                # Deduplication via database unique_together constraint check
                if FeedItem.objects.filter(source=source, guid=entry['guid']).exists():
                    continue

                # Generate 768-d embedding
                embedding_vector = generate_embedding(entry['content'])
                
                # Evaluate against the 4 Axioms
                best_axiom = FeedItem.AxiomChoices.UNASSIGNED
                best_score = 0.0

                for axiom, centroid_vector in centroids.items():
                    score = cosine_similarity(embedding_vector, centroid_vector)
                    if score > best_score:
                        best_score = score
                        best_axiom = axiom

                # The Closed-World Assumption Threshold
                if best_score >= SIMILARITY_THRESHOLD:
                    FeedItem.objects.create(
                        workspace_id=source.workspace_id,
                        source=source,
                        guid=entry['guid'],
                        title=entry['title'],
                        url=entry['url'],
                        content=entry['content'],
                        published_at=entry['published_at'],
                        embedding=embedding_vector,
                        category=best_axiom,
                        similarity_score=best_score,
                        state=FeedItem.StateChoices.ACTIONABLE
                    )
                    new_items_count += 1

        # 4. Finalize state
        _update_polling_decay(source, success=(new_items_count > 0))


def _update_polling_decay(source: FeedSource, success: bool) -> None:
    """Adjusts the polling interval based on axiomatic discovery."""
    source.last_polled_at = timezone.now()
    
    if success:
        source.consecutive_empty_polls = 0
    else:
        source.consecutive_empty_polls += 1

    source.next_poll_at = calculate_next_poll_time(
        source.base_poll_interval, 
        source.max_poll_interval, 
        source.consecutive_empty_polls
    )
    source.save(update_fields=['last_polled_at', 'consecutive_empty_polls', 'next_poll_at'])
