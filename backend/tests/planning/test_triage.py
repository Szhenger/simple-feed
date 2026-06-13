import pytest
from unittest.mock import patch
from planning.models import EventManifest, LogisticsSnapshot
from workers.planning_triage import triage_life_events
from feeds.models import Workspace

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def emilia_manifest():
    ws = Workspace.objects.create(id="ws_pm", name="PM Board")
    return EventManifest.objects.create(
        id="trip_japan", workspace=ws, label="Tokyo Trip",
        destination_code="HND", origin_code="JFK",
        target_date_start="2026-10-01", target_date_end="2026-10-14",
        max_flight_price_usd=800.0,
        ai_reporting_directive="Check Yen exchange rate."
    )

@patch('workers.planning_triage.FrontierModelClient.generate_brief')
@patch('workers.planning_triage.GlobalLogisticsClient.get_destination_context')
@patch('workers.planning_triage.GlobalLogisticsClient.get_optimal_flight')
def test_agent_ignores_expensive_flights(mock_flight, mock_ctx, mock_llm, emilia_manifest):
    # SIMULATE: Flight is $1200 (Above PM's $800 threshold)
    mock_flight.return_value = {"price": 1200.0, "airline": "JAL"}
    
    triage_life_events()
    
    # Assert LLM was completely bypassed (saving compute)
    mock_llm.assert_not_called()
    assert LogisticsSnapshot.objects.count() == 0

@patch('workers.planning_triage.FrontierModelClient.generate_brief')
@patch('workers.planning_triage.GlobalLogisticsClient.get_destination_context')
@patch('workers.planning_triage.GlobalLogisticsClient.get_optimal_flight')
def test_agent_dispatches_report_on_target_price(mock_flight, mock_ctx, mock_llm, emilia_manifest):
    # SIMULATE: Flight drops to $750
    mock_flight.return_value = {"price": 750.0, "airline": "ANA"}
    mock_ctx.return_value = "Yen is weak."
    mock_llm.return_value = "* Favorable exchange rate confirmed."
    
    triage_life_events()
    
    # Assert snapshot was created successfully
    snapshot = LogisticsSnapshot.objects.first()
    assert snapshot is not None
    assert snapshot.lowest_fare_found == 750.0
    assert "Favorable exchange rate" in snapshot.ai_synthesized_brief
