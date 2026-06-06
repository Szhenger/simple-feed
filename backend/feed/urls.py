from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, FeedSourceViewSet, FeedItemViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'sources', FeedSourceViewSet, basename='feedsource')
router.register(r'items', FeedItemViewSet, basename='feeditem')

urlpatterns = [
    path('', include(router.urls)),
]
