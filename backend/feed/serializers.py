from rest_framework import serializers
from .models import Workspace, FeedSource, FeedItem

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

class FeedSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedSource
        fields = [
            'id', 'workspace', 'url', 'title', 'is_active', 
            'last_polled_at', 'next_poll_at'
        ]
        read_only_fields = ['id', 'last_polled_at', 'next_poll_at']

class FeedItemSerializer(serializers.ModelSerializer):
    # Strip heavy backend payloads like vectors out of the SPA payload
    class Meta:
        model = FeedItem
        fields = [
            'id', 'workspace', 'source', 'guid', 'title', 'url', 
            'content', 'published_at', 'state', 'category', 'similarity_score', 'created_at'
        ]
        read_only_fields = fields # FeedItems are mutated by the backend state engine, not the client
