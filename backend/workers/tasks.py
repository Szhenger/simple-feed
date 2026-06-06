from celery import shared_task
from django.utils import timezone
from workers.ingestion import process_feed_source
from feed.models import FeedSource

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enqueue_feed_ingestion(self, feed_source_id: str):
    """
    Idempotent task to process a single syndication stream.
    Retries up to 3 times on unhandled exceptions (e.g., transient DB drops).
    """
    try:
        process_feed_source(feed_source_id)
    except Exception as exc:
        # Let Celery handle the exponential backoff for actual execution failures
        raise self.retry(exc=exc)


@shared_task
def sweep_due_feeds():
    """
    Periodic orchestrator task. 
    Queries the database for feeds where the calculated `next_poll_at` timestamp 
    has passed, and distributes them across the worker fleet.
    """
    now = timezone.now()
    
    # Standard ORM query; index on `next_poll_at` is highly recommended in db/ddls
    due_sources = FeedSource.objects.filter(
        is_active=True, 
        next_poll_at__lte=now
    ).values_list('id', flat=True)

    for source_id in due_sources:
        enqueue_feed_ingestion.delay(str(source_id))
