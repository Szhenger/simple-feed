from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="user_profile")
    professional = models.CharField(max_length=280, blank=True)
    hobbies = models.CharField(max_length=280, blank=True)
    interests = models.CharField(max_length=280, blank=True)
    is_public = models.BooleanField(default=False)

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="user_feed")
    title = models.CharField(max_length=64, blank=False)
    home_page_url = models.URLField(max_length=500, blank=False)
    feed_url = models.URLField(max_length=500, blank=False)
    description = models.CharField(max_length=280, blank=True)
    user_comment = models.CharField(max_length=140, blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "title", "home_page_url", "feed_url")

class Item(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, blank=False, related_name="feed_item")
    title = models.CharField(max_length=64, blank=True)
    url = models.URLField(max_length=500, blank=False)
    content = models.TextField(blank=True)
    date_published = models.DateTimeField(blank=True)