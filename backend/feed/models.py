import uuid
from django.db import models
from django.conf import settings
from pgvector.django import VectorField

class Workspace(models.Model):
    """
    The strict isolation boundary for a multi-tenant environment.
    PostgreSQL RLS policies will enforce access control based on this ID.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_workspaces")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FeedSource(models.Model):
    """
    The syndication stream target, managed via an exponential polling decay mechanism.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="feed_sources")
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=255, blank=True)
    
    # Exponential Backoff Polling Mechanics
    base_poll_interval = models.IntegerField(default=60, help_text="T_base in minutes")
    max_poll_interval = models.IntegerField(default=1440, help_text="T_max in minutes (default 24h)")
    consecutive_empty_polls = models.IntegerField(default=0, help_text="n multiplier")
    last_polled_at = models.DateTimeField(null=True, blank=True)
    next_poll_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('workspace', 'url')

    def __str__(self):
        return self.title or self.url

class FeedItem(models.Model):
    """
    The granular unit of ingestion, passed through the AI triage pipeline
    and verified against the 4 Professional Axioms.
    """
    class StateChoices(models.TextChoices):
        DISCOVERED = 'DISCOVERED', 'Discovered'
        VECTOR_TRIAGED = 'VECTOR_TRIAGED', 'Vector Triaged'
        ACTIONABLE = 'ACTIONABLE', 'Actionable (User Workspace)'
        ARCHIVED = 'ARCHIVED', 'Archived / Completed'

    class AxiomChoices(models.TextChoices):
        EDUCATION = 'EDUCATION', 'Education'
        CAREER = 'CAREER', 'Career Advancement'
        FINANCE = 'FINANCE', 'Finances'
        LIFE = 'LIFE', 'Life Planning'
        UNASSIGNED = 'UNASSIGNED', 'Unassigned / Pending Triage'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="feed_items")
    source = models.ForeignKey(FeedSource, on_delete=models.CASCADE, related_name="items")
    
    # Core Data parsed by the C++20 Kernel
    guid = models.CharField(max_length=512, db_index=True)
    title = models.CharField(max_length=1000)
    url = models.URLField(max_length=2000)
    content = models.TextField()
    published_at = models.DateTimeField()

    # AI Triage & Classification Mechanics
    embedding = VectorField(dimensions=768, null=True, blank=True)
    state = models.CharField(max_length=20, choices=StateChoices.choices, default=StateChoices.DISCOVERED)
    category = models.CharField(max_length=20, choices=AxiomChoices.choices, default=AxiomChoices.UNASSIGNED)
    similarity_score = models.FloatField(null=True, blank=True, help_text="Cosine similarity score against centroid")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('source', 'guid')
        indexes = [
            models.Index(fields=['workspace', 'state']),
            models.Index(fields=['workspace', 'category']),
            models.Index(fields=['published_at']),
        ]

    def __str__(self):
        return self.title
