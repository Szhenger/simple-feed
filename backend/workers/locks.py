import redis
from contextlib import contextmanager
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# Initialize the Redis client strictly for distributed locking
redis_client = redis.from_url(settings.CELERY_BROKER_URL)

@contextmanager
def acquire_feed_lock(feed_source_id: str, lock_timeout: int = 300):
    """
    Implements a distributed lock for a specific FeedSource using Redis.
    Guarantees that a URL is processed by exactly one worker at any given time.
    """
    lock_key = f"simplefeed:lock:source:{feed_source_id}"
    lock = redis_client.lock(lock_key, timeout=lock_timeout)
    
    acquired = lock.acquire(blocking=False)
    try:
        if not acquired:
            logger.warning(f"Lock collision for FeedSource {feed_source_id}. Aborting task.")
            yield False
        else:
            yield True
    finally:
        if acquired:
            try:
                lock.release()
            except redis.exceptions.LockError:
                logger.error(f"Failed to release lock {lock_key}; it may have expired.")
