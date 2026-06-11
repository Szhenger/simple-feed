import pytest
from unittest.mock import patch, MagicMock
from workers.finance_triage import process_active_strategy

# Mock Strategy Model Structure
class MockStrategy:
    def __init__(self, ticker, indicator, operator, value, prompt):
        self.id = "strat_123"
        self.execution_pipeline = {
            "ticker": ticker,
            "quant_rule": {"indicator": indicator, "operator": operator, "value": value},
            "ai_rule": {"prompt": prompt}
        }
        self.last_triggered_at = None
        
    def save(self, *args, **kwargs):
        pass

@pytest.fixture
def mock_strategy():
    return MockStrategy("XLV", "Z_SCORE", "<", -2.0, "Analyze macro.")

@patch('workers.finance_triage.HybridStrategy.objects.get')
@patch('workers.finance_triage.get_price_data')
@patch('workers.finance_triage.NativeQuantEngine.calculate_z_score')
@patch('workers.finance_triage.get_recent_news')
@patch('workers.finance_triage.FrontierModelClient')
def test_worker_halts_when_quant_fails(
    mock_llm_client, mock_get_news, mock_z_score, mock_get_price, mock_db_get, mock_strategy
):
    mock_db_get.return_value = mock_strategy
    mock_get_price.return_value = [100.0, 101.0, 99.0]
    
    # SIMULATE: C++ Kernel returns a normal Z-Score (-0.5), which is NOT < -2.0
    mock_z_score.return_value = -0.5
    
    result = process_active_strategy("strat_123")
    
    # Assert pipeline stops early and does NOT call external APIs
    assert result["status"] == "quant_failed"
    mock_get_news.assert_not_called()
    mock_llm_client.assert_not_called()

@patch('workers.finance_triage.HybridStrategy.objects.get')
@patch('workers.finance_triage.get_price_data')
@patch('workers.finance_triage.NativeQuantEngine.calculate_z_score')
@patch('workers.finance_triage.get_recent_news')
@patch('workers.finance_triage.FrontierModelClient')
def test_worker_triggers_ai_and_completes(
    mock_llm_client, mock_get_news, mock_z_score, mock_get_price, mock_db_get, mock_strategy
):
    mock_db_get.return_value = mock_strategy
    mock_get_price.return_value = [100.0, 101.0, 80.0]  # Sharp drop
    mock_get_news.return_value = ["CEO resigns"]
    
    # SIMULATE: C++ Kernel returns extreme Z-score (-3.5), passing the math check
    mock_z_score.return_value = -3.5
    
    # SIMULATE: LLM Client returns positive sentiment trigger
    mock_llm_instance = MagicMock()
    mock_llm_instance.evaluate_sentiment.return_value = {
        "trigger_alert": True, 
        "rationale": "Systemic risk confirmed."
    }
    mock_llm_client.return_value = mock_llm_instance
    
    result = process_active_strategy("strat_123")
    
    # Assert full pipeline executed
    assert result["status"] == "completed"
    assert result["action_taken"] is True
    mock_llm_instance.evaluate_sentiment.assert_called_once()
