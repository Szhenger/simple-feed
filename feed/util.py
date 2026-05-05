"""
ingestion.py — Feed ingestion worker.

Design decisions
----------------
* parse_date()        — centralises all date-parsing logic with a fallback chain,
                        eliminating duplicated try/except blocks.
* get_items()         — uses bulk_create + ignore_conflicts instead of per-item save(),
                        eliminating N DB round-trips and making re-runs idempotent.
* update_feeds()      — filters to is_active feeds only, runs each feed in its own
                        thread via ThreadPoolExecutor, and catches per-feed exceptions
                        so one broken feed cannot abort the entire job.
* run_scheduler()     — daemon thread + stop_event lets the host process shut down
                        cleanly without hanging on thread.join().
* Module-level side effects (schedule / thread) are wrapped in start_scheduler() so
  the module is safely importable in tests and management commands without spawning
  threads.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import schedule

from .models import Feed, Item

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FEED_WORKERS = 8          # concurrent feed-fetch threads during update_feeds()
UPDATE_TIME      = "07:30"    # daily ingestion time (24-hour, server-local clock)
LOOKBACK_DAYS    = 1          # update_feeds() ignores items older than this

# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

# Ordered list of strptime format strings to try.
_DATE_FORMATS = (
    "%a, %d %b %Y %H:%M:%S %Z",   # e.g. "Mon, 01 Jan 2024 12:00:00 GMT"
    "%a, %d %b %Y %H:%M:%S %z",   # e.g. "Mon, 01 Jan 2024 12:00:00 +0000"
    "%Y-%m-%dT%H:%M:%S%z",        # ISO 8601 with tz  (Atom)
    "%Y-%m-%dT%H:%M:%SZ",         # ISO 8601 UTC      (Atom)
    "%Y-%m-%d %H:%M:%S",          # bare datetime
)


def parse_date(raw: str | None) -> datetime | None:
    """
    Return an aware datetime from a raw feed date string, or None on failure.

    Strategy
    --------
    1. Try email.utils.parsedate_to_datetime — handles almost all RFC 2822
       variants more reliably than strptime.
    2. Fall back through _DATE_FORMATS with strptime.
    3. Return None rather than raise so callers can decide how to handle missing dates.
    """
    if not raw:
        return None

    # Preferred: RFC 2822 parser from the stdlib (handles timezone names too)
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        pass

    # Fallback chain
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            # Make naive datetimes explicitly UTC so Django doesn't complain
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    logger.warning("parse_date: unrecognised format %r", raw)
    return None


# ---------------------------------------------------------------------------
# Core ingestion helpers
# ---------------------------------------------------------------------------

def _entry_to_item(entry, feed: Feed) -> Item | None:
    """
    Convert a feedparser entry dict to an unsaved Item, or None if the
    entry is missing a URL (the only field we treat as mandatory).
    """
    url = getattr(entry, "link", None)
    if not url:
        return None

    return Item(
        feed=feed,
        title=(getattr(entry, "title",       None) or "")[:256],
        url=url,
        content=getattr(entry, "description", None) or getattr(entry, "summary", "") or "",
        date_published=parse_date(getattr(entry, "published", None)),
    )


def get_items(feed: Feed) -> int:
    """
    Fetch all entries for *feed* and persist them.

    Uses bulk_create(ignore_conflicts=True) so:
    * Only one DB round-trip instead of one per item.
    * Re-running on the same feed is idempotent (relies on Item's
      unique_together = ('feed', 'url') from models.py).

    Returns the number of rows actually inserted.
    """
    try:
        parsed = feedparser.parse(feed.feed_url)
    except Exception as exc:
        logger.error("get_items: feedparser failed for feed %s: %s", feed.id, exc)
        return 0

    if parsed.bozo and parsed.bozo_exception:
        logger.warning(
            "get_items: feed %s is malformed (%s) — attempting anyway",
            feed.id, parsed.bozo_exception,
        )

    # Reverse so oldest entries are inserted first (preserves chronological PK order)
    entries = list(reversed(parsed.entries))
    items = [item for e in entries if (item := _entry_to_item(e, feed)) is not None]

    if not items:
        return 0

    created = Item.objects.bulk_create(items, ignore_conflicts=True)
    logger.info("get_items: feed %s — %d new item(s) inserted", feed.id, len(created))
    return len(created)


def _update_single_feed(feed: Feed, lookback: datetime) -> int:
    """
    Fetch recent entries for one feed and persist any that are new.
    Called from a worker thread inside update_feeds().
    Returns the number of rows inserted.
    """
    try:
        parsed = feedparser.parse(feed.feed_url)
    except Exception as exc:
        logger.error("update_feeds: feedparser failed for feed %s: %s", feed.id, exc)
        return 0

    if parsed.bozo and parsed.bozo_exception:
        logger.warning(
            "update_feeds: feed %s is malformed (%s) — attempting anyway",
            feed.id, parsed.bozo_exception,
        )

    recent_items = []
    for entry in reversed(parsed.entries):
        item = _entry_to_item(entry, feed)
        if item is None:
            continue
        # Keep entries that are recent or have no date (rather than silently drop them)
        if item.date_published is None or item.date_published >= lookback:
            recent_items.append(item)

    if not recent_items:
        return 0

    created = Item.objects.bulk_create(recent_items, ignore_conflicts=True)
    logger.info(
        "update_feeds: feed %s — %d new item(s) inserted", feed.id, len(created)
    )
    return len(created)


def update_feeds() -> None:
    """
    Scheduled job: refresh all active feeds in parallel.

    * Skips inactive feeds (is_active=False).
    * Uses ThreadPoolExecutor so slow/hanging HTTP fetches don't block each other.
    * Catches and logs per-feed exceptions so one bad feed cannot abort the job.
    """
    lookback = datetime.now(tz=timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    feeds = list(Feed.objects.filter(is_active=True))

    if not feeds:
        logger.info("update_feeds: no active feeds found")
        return

    logger.info("update_feeds: refreshing %d active feed(s)", len(feeds))
    total_inserted = 0

    with ThreadPoolExecutor(max_workers=MAX_FEED_WORKERS) as pool:
        futures = {
            pool.submit(_update_single_feed, feed, lookback): feed
            for feed in feeds
        }
        for future in as_completed(futures):
            feed = futures[future]
            try:
                total_inserted += future.result()
            except Exception as exc:
                # Belt-and-suspenders: _update_single_feed already catches internally,
                # but we guard here in case of unexpected errors (e.g. DB issues).
                logger.error(
                    "update_feeds: unhandled error for feed %s: %s", feed.id, exc
                )

    logger.info("update_feeds: job complete — %d total new item(s)", total_inserted)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

_stop_event  = threading.Event()
_scheduler_thread: threading.Thread | None = None


def _run_scheduler() -> None:
    """Target for the scheduler thread. Exits cleanly when _stop_event is set."""
    logger.info("scheduler: started (update scheduled at %s daily)", UPDATE_TIME)
    while not _stop_event.is_set():
        schedule.run_pending()
        # Sleep in short increments so stop_event is checked frequently
        _stop_event.wait(timeout=30)
    logger.info("scheduler: stopped")


def start_scheduler() -> None:
    """
    Register the daily job and start the background scheduler thread.

    Call this once from AppConfig.ready() — not at module import time —
    so the thread is never spawned during tests or management commands
    unless you explicitly want it.

        # yourapp/apps.py
        class YourAppConfig(AppConfig):
            def ready(self):
                from .ingestion import start_scheduler
                start_scheduler()
    """
    global _scheduler_thread

    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.warning("start_scheduler: scheduler is already running")
        return

    _stop_event.clear()
    schedule.every().day.at(UPDATE_TIME).do(update_feeds)

    _scheduler_thread = threading.Thread(
        target=_run_scheduler,
        name="feed-scheduler",
        daemon=True,   # won't block process exit
    )
    _scheduler_thread.start()


def stop_scheduler() -> None:
    """
    Signal the scheduler thread to exit and wait for it to finish.
    Useful in tests and graceful-shutdown hooks.
    """
    _stop_event.set()
    if _scheduler_thread:
        _scheduler_thread.join(timeout=5)
