import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from finance.models import HybridStrategy
from feeds.models import Workspace

# Enforce real database transactions and inline Celery execution
pytestmark = pytest.mark.django_db(transaction=True)

class TestFinanceEndToEndPipeline:
    
    @pytest.fixture(autouse=True)
    def setup_tenant(self):
        self.workspace = Workspace.objects.create(id="ws_brick_med", name="Brick's Terminal")
        self.client = APIClient()
        self.client.defaults['HTTP_X_WORKSPACE_ID'] = self.workspace.id

    @patch('workers.finance_triage.get_price_data')
    @patch('workers.finance_triage.FrontierModelClient.evaluate_sentiment')
    def test_full_strategy_deployment_and_execution_loop(
        self, mock_ai_eval, mock_price_feed, settings
    ):
        """
        Simulates the entire user journey:
        1. User deploys a strategy via the API.
        2. Backend compiles the DAG and persists it.
        3. Celery automatically executes the strategy using the C++ kernel.
        """
        # Force Celery to execute synchronously in the test
        settings.CELERY_TASK_ALWAYS_EAGER = True
        
        # 1. Mock the external data dependencies
        # Simulate a massive crash in Apple stock
        mock_price_feed.return_value = [150.0] * 19 + [100.0] 
        mock_ai_eval.return_value = {
            "trigger_alert": True,
            "rationale": "Apple VR headset delayed. Macro intact."
        }

        # 2. Simulate the UI sending the React Flow JSON to the Django API
        url = reverse('deploy-strategy')
        ui_payload = {
            "graph_id": "strat_e2e_001",
            "nodes": [
                {"id": "n1", "type": "asset", "data": {"ticker": "AAPL"}},
                {"id": "n2", "type": "quant", "data": {"indicator": "Z_SCORE", "operator": "<", "value": -2.0}},
                {"id": "n3", "type": "ai", "data": {"prompt": "Is the thesis broken?"}}
            ],
            "connections": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"}
            ]
        }

        # 3. Fire the request
        response = self.client.post(url, ui_payload, format='json')
        
        # 4. Verify API accepted and compiled the graph
        assert response.status_code == status.HTTP_201_CREATED
        
        # 5. Verify database state
        strategy = HybridStrategy.objects.get(id="strat_e2e_001")
        assert strategy.asset_ticker == "AAPL"
        
        # 6. Manually trigger the Celery beat task to execute the strategy
        from workers.finance_triage import process_active_strategy
        result = process_active_strategy(strategy.id)
        
        # 7. Verify the complete pipeline
        assert result["status"] == "completed"
        assert result["action_taken"] is True
        
        # Ensure the LLM was called with the Intent Expander's injected text
        ai_call_args = mock_ai_eval.call_args[0][0]
        assert "Is the thesis broken?" in ai_call_args
        assert "structural breakdown in corporate fundamentals" in ai_call_args # Fallback heuristic
