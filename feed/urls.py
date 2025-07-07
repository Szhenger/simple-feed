from django.urls import path
from . import views

# Create your URLs here.

urlpatterns = [
    path("", views.index_view, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("new_feed", views.new_feed_view, name="new_feed"),
    path("profile/<int:user_id>", views.profile_view, name="profile"),
    path("profile_edit", views.profile_edit_view, name="edit"),
    path("profile_public/<int:profile_id>", views.profile_public_view, name="profile_public"),
    path("feed/<int:feed_id>", views.feed_view, name="feed"),
    path("feed_edit", views.feed_edit_view, name="feed_edit"),
    path("feed_active/<int:feed_id>", views.feed_active_view, name="feed_active"),
    path("feed_delete/<int:feed_id>", views.feed_delete_view, name="feed_delete"),
    path("feed_public/<int:feed_id>", views.feed_public_view, name="feed_public"),
    path("item/<int:item_id>", views.item_view, name="item"),
    path("item_delete/<int:item_id>", views.item_delete_view, name="item_delete"),
    path("random", views.random_view, name="random")
]
