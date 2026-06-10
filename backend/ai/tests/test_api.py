import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

@pytest.mark.ai_subsystem
class TestAIEndpointMatrix(APITestCase):

    def setUp(self):
        # Establish workspace-tenant credentials for API authorization headers
        self.workspace_id = "ws_ai_test"
        self.client.defaults['HTTP_X_WORKSPACE_ID'] = self.workspace_id
        
        # Superuser/Staff bypass authentication for local microservice calls
        # (Assuming custom tenant authorization middleware is active)
        
    @patch('ai.views.TransformerSingleton.get_embedding')
    def test_embedding_endpoint_returns_correct_vector_dimensions(self, mock_get_embedding):
        """
        Verifies that a valid string payload maps cleanly to a 768-D array structure.
        """
        # Generate a mock 768-dimensional float array
        synthetic_vector = [0.015] * 768
        mock_get_embedding.return_value = synthetic_vector

        url = reverse('ai-embed')
        payload = {"text": "Axiomatic validation of high-throughput vector tracking systems."}
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert "embedding" in response.data
        assert len(response.data["embedding"]) == 768
        assert response.data["embedding"][0] == 0.015
        mock_get_embedding.assert_called_once_with(payload["text"])

    def test_embedding_endpoint_rejects_empty_payload(self):
        """
        Ensures the API controller rejects empty or structurally invalid texts before calling models.
        """
        url = reverse('ai-embed')
        payload = {"text": ""}
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "text" in response.data

    @patch('ai.views.TransformerSingleton.compute_cosine_similarity')
    def test_similarity_endpoint_calculates_metric_bounds(self, mock_similarity):
        """
        Validates the math evaluation layer over the vector comparison endpoint.
        """
        mock_similarity.return_value = 0.892
        url = reverse('ai-similarity')
        
        payload = {
            "vector_a": [0.1] * 768,
            "vector_b": [0.2] * 768
        }
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert "similarity" in response.data
        assert response.data["similarity"] == 0.892

    def test_similarity_endpoint_enforces_dimensional_parity(self):
        """
        Edge Case: Rejects comparison calculations if vectors have mismatched sizes.
        """
        url = reverse('ai-similarity')
        payload = {
            "vector_a": [0.1] * 768,
            "vector_b": [0.2] * 512  # Mismatched dimension
        }
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Vector dimensions must match exactly" in response.data["error"]

    @patch('ai.views.TransformerSingleton.evaluate_triage')
    def test_triage_endpoint_applies_workspace_axioms_pass(self, mock_triage):
        """
        Verifies that texts meeting or exceeding the boundary rule receive a pass status.
        """
        # Mocking calculation outcome to simulate a passed score
        mock_triage.return_value = {"score": 0.784, "passed": True}
        
        url = reverse('ai-triage')
        payload = {"text": "High relevance production system documentation node."}
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "passed"
        assert response.data["score"] >= 0.72

    @patch('ai.views.TransformerSingleton.evaluate_triage')
    def test_triage_endpoint_applies_workspace_axioms_fail(self, mock_triage):
        """
        Verifies that low-scoring entities are accurately flagged for drop rules.
        """
        # Mocking calculation outcome to simulate a failed score
        mock_triage.return_value = {"score": 0.412, "passed": False}
        
        url = reverse('ai-triage')
        payload = {"text": "Irrelevant spam string payload."}
        
        response = self.client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "dropped"
        assert response.data["score"] < 0.72
