import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class FeedSynthesizer:
    @staticmethod
    def broadcast_event(workspace_id: str, pillar: str, title: str, payload: dict, priority: int = 1):
        """
        Publishes a real-time event to the Redis Pub/Sub channel for a specific workspace.
        
        :param pillar: 'EDUCATION', 'FINANCE', or 'PLANNING'
        :param priority: 1 (Standard) to 3 (Critical Alert, e.g., Market Crash)
        """
        channel = f"feed_ws_{workspace_id}"
        message = {
            "type": "feed.update",
            "data": {
                "pillar": pillar,
                "title": title,
                "payload": payload,
                "priority": priority,
                "timestamp": __import__('time').time()
            }
        }
        
        try:
            # We use the underlying Redis connection from Django's cache
            redis_client = cache.client.get_client()
            redis_client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to push event to Feed: {str(e)}")
