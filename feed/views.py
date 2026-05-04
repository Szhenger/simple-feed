"""
feed/views.py

Shard-aware views for the simplefeed application.

Query routing:
  - Pass hints={"shard_key": user.id} on Feed/Item/Profile queries so
    ShardRouter pins each user's data to a stable shard.
  - Read-heavy views (feed_view, item_view, random_view) get replica
    reads automatically via ShardRouter's REPLICA_READ_PROBABILITY.
  - All writes go to shard primaries — no hints needed for writes,
    ShardRouter handles that in db_for_write().
"""

from __future__ import annotations

import json
import logging
from random import choice
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import (
    HttpRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Feed, Item, Profile, User
from .util import get_items

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_body(request: HttpRequest) -> dict[str, Any]:
    """Safely parse a JSON request body; raises ValueError on bad input."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid JSON body") from exc


def _owned_feed(feed_id: int, user: User) -> Feed:
    """Return feed by PK, scoped to the owner's shard. 403 if not owner."""
    feed = get_object_or_404(
        Feed.objects.using("shard_%d" % _shard_id(user.id)),
        pk=feed_id,
    )
    if feed.user_id != user.id:
        raise PermissionError
    return feed


def _shard_id(user_id: int) -> int:
    """Mirror manage.get_shard_id() locally to avoid a circular import."""
    import hashlib
    from django.conf import settings

    shard_count = getattr(settings, "SHARD_COUNT", 3)
    digest = hashlib.sha256(str(user_id).encode()).hexdigest()
    return int(digest, 16) % shard_count


def _shard_hints(user_id: int) -> dict[str, int]:
    return {"shard_key": user_id}


# ── Auth views ────────────────────────────────────────────────────────────────

def index_view(request: HttpRequest):
    if not request.user.is_authenticated:
        return render(request, "feed/index.html")

    feeds = Feed.objects.filter(
        user=request.user,
    ).using(
        "shard_%d" % _shard_id(request.user.id)
    ).order_by("-id")

    return render(request, "feed/index.html", {
        "active_feeds": feeds.filter(is_active=True),
        "inactive_feeds": feeds.filter(is_active=False),
    })


@require_POST
def register_view(request: HttpRequest):
    try:
        data = _parse_body(request)
        username = data["username"]
        email = data["email"]
        password = data["password"]
    except (ValueError, KeyError):
        return JsonResponse(
            {"message": "Bad request.", "is_authenticated": False}, status=400
        )

    try:
        user = User.objects.create_user(username, email, password)
    except IntegrityError:
        logger.info("Registration collision for username=%r", username)
        return JsonResponse(
            {"message": "Username already taken.", "is_authenticated": False}
        )

    login(request, user)
    logger.info("New user registered: id=%d username=%r", user.id, user.username)
    return JsonResponse({"message": "Registered!", "is_authenticated": True})


@require_POST
def login_view(request: HttpRequest):
    try:
        data = _parse_body(request)
        username = data["username"]
        password = data["password"]
    except (ValueError, KeyError):
        return JsonResponse(
            {"message": "Bad request.", "is_authenticated": False}, status=400
        )

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({"message": "Logged in!", "is_authenticated": True})

    logger.info("Failed login attempt for username=%r", username)
    return JsonResponse({"message": "Invalid credentials.", "is_authenticated": False})


def logout_view(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# ── Feed views ────────────────────────────────────────────────────────────────

@login_required
@require_POST
def new_feed_view(request: HttpRequest):
    try:
        data = _parse_body(request)
        title = data["title"]
        home_page_url = data["home_page_url"]
        feed_url = data["feed_url"]
        description = data["description"]
        comment = data["comment"]
    except (ValueError, KeyError):
        return JsonResponse(
            {"message": "Bad request.", "is_feed": False}, status=400
        )

    try:
        feed = Feed.objects.create(
            title=title,
            home_page_url=home_page_url,
            feed_url=feed_url,
            description=description,
            user=request.user,
            user_comment=comment,
        )
    except IntegrityError:
        logger.warning("Feed creation failed for user_id=%d url=%r", request.user.id, feed_url)
        return JsonResponse({"message": "Failed to create feed.", "is_feed": False})

    get_items(feed)
    logger.info("Feed created: id=%d user_id=%d", feed.id, request.user.id)
    return JsonResponse({"message": "Feed live!", "is_feed": True})


@login_required
@require_POST
def feed_edit_view(request: HttpRequest):
    try:
        data = _parse_body(request)
        feed_id = int(data["id"])
        title = data["title"]
        home_page_url = data["home_page_url"]
        feed_url = data["feed_url"]
        description = data["description"]
        comment = data["comment"]
    except (ValueError, KeyError):
        return JsonResponse(
            {"message": "Bad request.", "is_edited": False}, status=400
        )

    try:
        feed = _owned_feed(feed_id, request.user)
    except PermissionError:
        return JsonResponse({"message": "Not your feed.", "is_edited": False}, status=403)

    feed.title = title
    feed.home_page_url = home_page_url
    feed.feed_url = feed_url
    feed.description = description
    feed.user_comment = comment
    feed.save()
    return JsonResponse({"message": "Feed updated!", "is_edited": True})


@login_required
def feed_delete_view(request: HttpRequest, feed_id: int):
    try:
        feed = _owned_feed(feed_id, request.user)
    except PermissionError:
        return HttpResponseForbidden()
    feed.delete()
    return HttpResponseRedirect(reverse("index"))


@login_required
def feed_active_view(request: HttpRequest, feed_id: int):
    try:
        feed = _owned_feed(feed_id, request.user)
        feed.is_active = not feed.is_active
        feed.save()
    except PermissionError:
        pass  # silently ignore — redirect either way
    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))


@login_required
def feed_public_view(request: HttpRequest, feed_id: int):
    try:
        feed = _owned_feed(feed_id, request.user)
        feed.is_public = not feed.is_public
        feed.save()
    except PermissionError:
        pass
    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))


def feed_view(request: HttpRequest, feed_id: int):
    feed = get_object_or_404(Feed, pk=feed_id)

    if not feed.is_public and (
        not request.user.is_authenticated or feed.user_id != request.user.id
    ):
        return HttpResponseRedirect(reverse("index"))

    items = (
        Item.objects.filter(feed=feed)
        .using("shard_%d_replica" % _shard_id(feed.user_id))
        .order_by("-id")
    )
    return render(request, "feed/feed.html", {"feed": feed, "items": items})


# ── Profile views ─────────────────────────────────────────────────────────────

def profile_view(request: HttpRequest, user_id: int):
    profile = get_object_or_404(
        Profile.objects.using("shard_%d" % _shard_id(user_id)),
        pk=user_id,
    )

    if not profile.is_public and (
        not request.user.is_authenticated or profile.user_id != request.user.id
    ):
        return HttpResponseRedirect(reverse("index"))

    return render(request, "feed/profile.html", {"profile": profile})


@login_required
@require_POST
def profile_edit_view(request: HttpRequest):
    try:
        data = _parse_body(request)
        professional = data["professional"]
        hobbies = data["hobbies"]
        interests = data["interests"]
    except (ValueError, KeyError):
        return JsonResponse({"message": "Bad request."}, status=400)

    profile, created = Profile.objects.using(
        "shard_%d" % _shard_id(request.user.id)
    ).update_or_create(
        pk=request.user.id,
        defaults={
            "user": request.user,
            "professional": professional,
            "hobbies": hobbies,
            "interests": interests,
        },
    )
    action = "created" if created else "updated"
    logger.info("Profile %s for user_id=%d", action, request.user.id)
    return JsonResponse({"message": "Profile saved.", "data": data})


@login_required
def profile_public_view(request: HttpRequest, profile_id: int):
    profile = get_object_or_404(
        Profile.objects.using("shard_%d" % _shard_id(request.user.id)),
        pk=profile_id,
    )
    if profile.user_id == request.user.id:
        profile.is_public = not profile.is_public
        profile.save()
    return HttpResponseRedirect(reverse("profile", kwargs={"user_id": profile.user_id}))


# ── Item views ────────────────────────────────────────────────────────────────

def item_view(request: HttpRequest, item_id: int):
    item = get_object_or_404(Item, pk=item_id)

    if not item.feed.is_public and (
        not request.user.is_authenticated or item.feed.user_id != request.user.id
    ):
        return HttpResponseRedirect(reverse("index"))

    return render(request, "feed/item.html", {"item": item})


@login_required
def item_delete_view(request: HttpRequest, item_id: int):
    item = get_object_or_404(Item, pk=item_id)
    feed_id = item.feed_id

    if item.feed.user_id == request.user.id:
        item.delete()
    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))


# ── Discovery ─────────────────────────────────────────────────────────────────

def random_view(request: HttpRequest):
    """Pick a random public feed and render it. Falls back to index if none exist."""
    feed_ids = list(Feed.objects.filter(is_public=True).values_list("id", flat=True))

    if not feed_ids:
        return HttpResponseRedirect(reverse("index"))

    feed_id = choice(feed_ids)
    feed = get_object_or_404(Feed, pk=feed_id)
    items = (
        Item.objects.filter(feed=feed)
        .using("shard_%d_replica" % _shard_id(feed.user_id))
        .order_by("-id")
    )
    return render(request, "feed/feed.html", {"feed": feed, "items": items})
