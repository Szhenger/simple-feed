from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Workspace, FeedSource, FeedItem
from .serializers import WorkspaceSerializer, FeedSourceSerializer, FeedItemSerializer

class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    Manages Workspace boundaries. Users can only interact with their own workspaces.
    """
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Enforce tenant isolation at the ORM level (RLS will serve as the secondary DB-level guard)
        return Workspace.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FeedSourceViewSet(viewsets.ModelViewSet):
    """
    CRUD for syndication targets. Creating a source here will trigger the initial Celery ingestion task.
    """
    serializer_class = FeedSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FeedSource.objects.filter(workspace__owner=self.request.user)

    def perform_create(self, serializer):
        # The frontend will pass the workspace_id. We ensure it belongs to the user.
        workspace_id = self.request.data.get('workspace')
        workspace = Workspace.objects.get(id=workspace_id, owner=self.request.user)
        instance = serializer.save(workspace=workspace)
        
        # TODO: Enqueue Celery Task here -> enqueue_feed_ingestion.delay(instance.id)


class FeedItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only view for the React SPA. The state transitions happen asynchronously in the background.
    """
    serializer_class = FeedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = FeedItem.objects.filter(workspace__owner=self.request.user)
        
        # Allow the TanStack Query frontend to filter by category and state
        state = self.request.query_params.get('state')
        category = self.request.query_params.get('category')
        
        if state:
            queryset = queryset.filter(state=state)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset.order_by('-published_at')
