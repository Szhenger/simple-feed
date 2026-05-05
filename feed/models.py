"""
models.py — RSS reader domain models.

Design decisions
----------------
* AbstractUser extension keeps auth flexible (add fields later without migrations hell).
* OneToOneField for Profile — a user has exactly one profile; ForeignKey allowed duplicates.
* Explicit __str__ on every model for admin/shell legibility.
* db_index / select_related-friendly FK naming.
* Timestamps (created_at / updated_at) on every mutable model via TimestampedModel.
* Item deduplication via unique_together on (feed, url) — prevents re-ingestion.
* TextField for Item.content — no arbitrary length cap on article bodies.
* date_published allows null/blank — not all feeds provide it reliably.
* is_active / is_public use explicit BooleanField defaults.
* Meta.indexes added for the query patterns most readers will hit at scale.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class TimestampedModel(models.Model):
    """Mixin that stamps created_at / updated_at on every subclass."""

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class User(AbstractUser):
    """
    Thin AbstractUser subclass — exists so we can add fields later
    (e.g. email-only auth, MFA flag) without cross-app migrations.
    Always set AUTH_USER_MODEL = 'yourapp.User' in settings.py.
    """

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return self.username


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class Profile(TimestampedModel):
    """
    One-to-one extension of User for non-auth attributes.

    OneToOneField (not ForeignKey) enforces the one-profile-per-user
    invariant at the database level and gives you user.profile reverse access.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    professional = models.CharField(max_length=280, blank=True)
    hobbies = models.CharField(max_length=280, blank=True)
    interests = models.CharField(max_length=280, blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"Profile({self.user})"


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------

class Feed(TimestampedModel):
    """
    An RSS/Atom feed subscription owned by a user.

    Uniqueness is enforced on (user, feed_url) only — the same logical feed
    should not be subscribed to twice regardless of how the user labels it.
    home_page_url and title can drift over time; feed_url is the stable key.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feeds",
    )
    title = models.CharField(max_length=64)
    home_page_url = models.URLField(max_length=500)
    feed_url = models.URLField(max_length=500)
    description = models.CharField(max_length=280, blank=True)
    user_comment = models.CharField(max_length=140, blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "feed"
        verbose_name_plural = "feeds"
        # A user cannot subscribe to the same feed URL twice.
        unique_together = ("user", "feed_url")
        indexes = [
            # Fast lookup of all active feeds (used by the ingestion worker).
            models.Index(fields=["is_active"], name="feed_is_active_idx"),
            # Fast lookup of a user's feeds.
            models.Index(fields=["user", "is_active"], name="feed_user_active_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.title} → {self.user}"


# ---------------------------------------------------------------------------
# Item
# ---------------------------------------------------------------------------

class Item(TimestampedModel):
    """
    A single entry / article ingested from a Feed.

    Deduplication key is (feed, url) — the same URL should not be stored
    twice for the same feed even if the ingestion job runs repeatedly.
    """

    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(max_length=256, blank=True)  # wider: titles can be long
    url = models.URLField(max_length=500)
    content = models.TextField(blank=True)
    date_published = models.DateTimeField(null=True, blank=True)  # not always present

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "items"
        unique_together = ("feed", "url")
        indexes = [
            # Chronological feed display — the dominant read pattern.
            models.Index(
                fields=["feed", "-date_published"],
                name="item_feed_date_idx",
            ),
        ]
        ordering = ["-date_published"]

    def __str__(self) -> str:
        return f"{self.title or self.url} ({self.feed})"
