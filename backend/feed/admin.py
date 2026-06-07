from django.contrib import admin
from .models import Workspace, FeedSource, FeedItem

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(FeedSource)
class FeedSourceAdmin(admin.ModelAdmin):
    list_display = ('url', 'workspace', 'is_active', 'last_polled_at', 'next_poll_at')
    list_filter = ('is_active',)

@admin.register(FeedItem)
class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'workspace', 'category', 'similarity_score', 'state', 'published_at')
    list_filter = ('state', 'category')
    search_fields = ('title', 'guid')
    
    # CRITICAL: Exclude the embedding from the UI to prevent browser crashes,
    # or make it read-only if you wish to visually inspect the array.
    exclude = ('embedding',) 
    readonly_fields = ('similarity_score', 'published_at')
