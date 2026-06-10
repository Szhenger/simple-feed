import pytest
from django.urls import reverse
from rest_framework.test import APIClient

# Force pytest to grant database access to this test module
pytestmark = pytest.mark.django_db

class TestGatewaySecurity:
    
    def test_anonymous_requests_are_rejected(self):
        """Ensure the API acts as a strict gatekeeper against unauthenticated hits."""
        client = APIClient()
        url = reverse('api-feed-list')
        
        response = client.get(url)
        assert response.status_code == 401
        assert response.json()['detail'] == "Authentication credentials were not provided."

    def test_workspace_context_enforces_row_level_security(self, django_user_model):
        """Verify that a user in Workspace A cannot query vectors from Workspace B."""
        # 1. Setup minimal users and workspaces
        user_a = django_user_model.objects.create(username="tenant_a", workspace_id="ws_001")
        user_b = django_user_model.objects.create(username="tenant_b", workspace_id="ws_002")
        
        client = APIClient()
        client.force_authenticate(user=user_a)
        
        # 2. Attempt to explicitly request Tenant B's data via the API
        url = reverse('api-feed-list')
        response = client.get(url, HTTP_X_WORKSPACE_ID="ws_002")
        
        # 3. The gateway should mathematically reject the cross-tenant request
        assert response.status_code == 403
        assert "Workspace context mismatch" in str(response.content)
