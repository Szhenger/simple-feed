from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json
from random import choice
from .models import User, Profile, Feed, Item
from .util import get_items

# Create your views here.


def index_view(request):
    if request.user.is_authenticated:

        # Get the feeds of user
        feeds = Feed.objects.filter(user=request.user)
        active_feeds = feeds.filter(is_active=True).order_by("id").reverse()
        inactive_feeds = feeds.filter(is_active=False).order_by("id").reverse()

        # Render the feeds
        return render(request, "feeds/index.html", {
            "active_feeds": active_feeds,
            "inactive_feeds": inactive_feeds
        })
    else:
        return render(request, "feeds/index.html")


def register_view(request):
    if request.method == "POST":

        # Gets username, email, password via a JavaScript POST fetch
        data = json.loads(request.body)
        username = data["username"]
        email = data["email"]
        password = data["password"]

        # Attempts to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return JsonResponse({"message": "Not Registered!", "is_authenticated": False})
        login(request, user)
        return JsonResponse({"message": "Registered!", "is_authenticated": True})
    else:
        return HttpResponseRedirect(reverse("index"))


def login_view(request):
    if request.method == "POST":

        # Gets usename and password via JavaScript POST fetch
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]

        # Attempt to log in user
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"message": "Logged In!", "is_authenticated": True})
        else:
            return JsonResponse({"message": "Not Logged In!", "is_authenticated": False})
    else:
        return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def new_feed_view(request):
    if request.method == "POST":

        # Gets title, homepage url, feed url, description, comment via a JavaScript POST fetch
        data = json.loads(request.body)
        title = data["title"]
        home_page_url = data["home_page_url"]
        feed_url = data["feed_url"]
        description = data["description"]
        user = User.objects.get(pk=request.user.id)
        comment = data["comment"]

        # Attempts to create new feed
        try:
            feed = Feed(
                title=title,
                home_page_url=home_page_url,
                feed_url=feed_url,
                description=description,
                user=user,
                user_comment=comment
            )
            feed.save()
        except IntegrityError:
            return JsonResponse({"message": "Failed to Create Feed", "is_feed": False})

        # Populates the new feed
        get_items(feed)
        return JsonResponse({"message": "Feed Live", "is_feed": True})
    else:
        return HttpResponseRedirect(reverse("index"))


def profile_view(request, user_id):

    # Gets the profile associated with the user of user_id
    profile = Profile.objects.get(pk=user_id)

    # Ensure that profile is public or the user is the owner of profile
    if profile.is_public == True or profile.user.id == request.user.id:
        return render(request, "feeds/profile.html", {
            "profile": profile
        })
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def profile_edit_view(request):
    if request.method == "POST":

        # Get decriptions via JavaScript POST fetch
        data = json.loads(request.body)
        professional = data["professional"]
        hobbies = data["hobbies"]
        interests = data["interests"]

        # Check whether user profile exists
        try:

            # Attempts to update user profile
            profile = Profile.objects.get(pk=request.user.id)
            profile.professional = professional
            profile.hobbies = hobbies
            profile.interests = interests
            profile.save()
        except:

            # Otherwise makes a new profile for user
            profile = Profile(
                user=request.user,
                professional=professional,
                hobbies=hobbies,
                interests=interests
            )
            profile.save()
        return JsonResponse({"message": "Profile Edited", "data": data})
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def profile_public_view(request, profile_id):
    profile = Profile.objects.get(pk=profile_id)

    # Ensures that the user is the owner of profile
    if profile.user.id == request.user.id:
        profile.is_public = not(profile.is_public)
        profile.save()

    return HttpResponseRedirect(reverse("profile", kwargs={"user_id": profile.user.id}))


def feed_view(request, feed_id):
    feed = Feed.objects.get(pk=feed_id)

    # Returns feed only when the feed is public or user is the owner
    if feed.is_public == True or feed.user.id == request.user.id:
        items = Item.objects.filter(feed=feed).order_by("id").reverse()
        return render(request, "feeds/feed.html", {
            "feed": feed,
            "items": items
        })
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def feed_edit_view(request):
    if request.method == "POST":

        # Gets new feed data via JavaScript POST fetch
        data = json.loads(request.body)
        id = data["id"]
        title = data["title"]
        home_page_url = data["home_page_url"]
        feed_url = data["feed_url"]
        description = data["description"]
        comment = data["comment"]

        # Attempts to get requested feed of user
        feed = Feed.objects.get(pk=id)
        if feed.user.id != request.user.id:
            return JsonResponse({"message": "Feed Not Changed!", "is_edited": False})
        feed.title = title
        feed.home_page_url = home_page_url
        feed.feed_url = feed_url
        feed.description = description
        feed.user_comment = comment
        feed.save()
        return JsonResponse({"message": "Feed Changed!", "is_edited": True})
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def feed_delete_view(request, feed_id):
    feed = Feed.objects.get(pk=feed_id)

    # Ensures that user is the owner of the feed
    if request.user.id != feed.user.id:
        return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))

    feed.delete()
    return HttpResponseRedirect(reverse("index"))


@login_required
def feed_active_view(request, feed_id):
    feed = Feed.objects.get(pk=feed_id)

    # Ensures that user is the owner of the feed
    if request.user.id == feed.user.id:

        # Changes the feed to be active
        feed.is_active = not(feed.is_active)
        feed.save()

    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))


@login_required
def feed_public_view(request, feed_id):
    feed = Feed.objects.get(pk=feed_id)

    # Ensures that user is the owner of the feed
    if request.user.id == feed.user.id:

        # Changes the feed to be public
        feed.is_public = not(feed.is_public)
        feed.save()

    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": feed_id}))


def item_view(request, item_id):
    item = Item.objects.get(pk=item_id)

    # Ensures that the item returned is public or user is the owner
    if item.feed.is_public == True or item.feed.user.id == request.user.id:
        return render(request, "feeds/item.html", {
            "item": item
        })
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def item_delete_view(request, item_id):
    item = Item.objects.get(pk=item_id)
    item_feed = item.feed

    # Ensure that user is the owner of the feed
    if item.feed.user.id == request.user.id:
        item.delete()
    return HttpResponseRedirect(reverse("feed", kwargs={"feed_id": item_feed.id }))

def random_view(request):
    try:

        # Randomly chooses a public feed to show
        feed_ids = Feed.objects.filter(is_public=True).values_list("id", flat=True)
        feed_id = choice(feed_ids)
        feed = Feed.objects.get(pk=feed_id)
        items = Item.objects.filter(feed=feed).order_by("id").reverse()
        return render(request, "feeds/feed.html", {
            "feed": feed,
            "items": items
        })
    except:

        # Render the index view
        return HttpResponseRedirect(reverse("index"))