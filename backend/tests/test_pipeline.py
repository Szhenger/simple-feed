import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from feeds.models import FeedItem, Workspace
from workers.tasks import process_inbound_feed_payload

# Use transaction=True to ensure real database commits occur, allowing
# multi-layered components to interact over actual state rows.
pytestmark = pytest.mark.django_db(transaction=True)

class TestSystemIntegrationPipeline:

    def test_end_to_end_ingestion_to_api_flow(self):
        """
        Validates the entire backend pipeline loop:
        1. Seed workspace tenant configuration.
        2. Simulate a live inbound raw feed ingestion task.
        3. Verify relational persistence layers.
        4. Request payload via REST API to ensure delivery format compliance.
        """
        # --- STAGE 1: Tenant Preparation ---
        workspace = Workspace.objects.create(
            id="ws_prod_sim", 
            name="Integrated Live Validation Terminal"
        )
        
        # --- STAGE 2: Execute Celery Pipeline Ingestion ---
        # Synthetic high-relevance RSS payload targeting a 2026 data partition
        sample_payload = {
            "guid": "unique-uuid-2026-xyz",
            "title": "State Persistence via Advanced Rust/Python FFI Boundaries",
            "content": "A high-performance analysis detailing zero-copy vector passing rules.",
            "published_at": "2026-06-10T12:00:00Z"
        }
        
        # Trigger the task inline (Eager mode routes this directly through the real AI parser)
        task_result = process_inbound_feed_payload(
            workspace_id=workspace.id, 
            payload=sample_payload
        )
        
        # Assert the business logic engine triaged the payload into a save execution status
        assert task_result["status"] == "persisted"
        assert task_result["item_guid"] == "unique-uuid-2026-xyz"

        # --- STAGE 3: Database Integrity Checks ---
        # Confirm the object physically exists in PostgreSQL with its vector embeddings populated
        db_item = FeedItem.objects.get(guid="unique-uuid-2026-xyz", workspace=workspace)
        assert db_item.title == sample_payload["title"]
        assert len(db_item.embedding) == 768  # Confirms AI model transformed data mid-pipeline

        # --- STAGE 4: API Gateway Resolution (Frontend Handshake) ---
        client = APIClient()
        
        # Authenticate current scope session to bypass tenant gatekeepers
        client.defaults['HTTP_X_WORKSPACE_ID'] = workspace.id
        
        url = reverse('api-feed-list')
        response = client.get(url)
        
        # Verify the API controller serializes the pipeline-generated data perfectly
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["guid"] == "unique-uuid-2026-xyz"
        assert response.data[0]["title"] == "State Persistence via Advanced Rust/Python FFI Boundaries"

    def test_concurrent_idempotency_triage_deduplication(self):
        """
        Verifies that the database and scheduling loop gracefully trap 
        duplicate identical records to prevent data duplication.
        """
        workspace = Workspace.objects.create(id="ws_dedup_test", name="Deduplication Terminal")
        
        duplicate_payload = {
            "guid": "duplicate-uuid-2026",
            "title": "Idempotency Loop Validation Check",
            "content": "Ensuring database unique constraints remain unbroken under worker stress.",
            "published_at": "2026-06-10T12:15:00Z"
        }

        # Fire the task sequentially to simulate back-to-back delivery ticks
        res_first = process_inbound_feed_payload(workspace.id, duplicate_payload)
        res_second = process_inbound_feed_payload(workspace.id, duplicate_payload)

        # The first loop should save the record normally
        assert res_first["status"] == "persisted"
        
        # The second loop should detect the existing unique hash and signal a graceful pass/skip
        assert res_second["status"] == "ignored_duplicate"
        assert FeedItem.objects.filter(guid="duplicate-uuid-2026", workspace=workspace).count() == 1
