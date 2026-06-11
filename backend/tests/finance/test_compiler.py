import pytest
from finance.compiler import compile_react_flow_dag, GraphCompilationError

@pytest.fixture
def valid_graph_payload():
    return {
        "nodes": [
            {"id": "n1", "type": "asset", "data": {"ticker": "XLV"}},
            {"id": "n2", "type": "quant", "data": {"indicator": "Z_SCORE", "operator": "<", "value": -2.0}},
            {"id": "n3", "type": "ai", "data": {"prompt": "Check macro."}}
        ],
        "edges": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"}
        ]
    }

def test_compile_valid_graph(valid_graph_payload):
    pipeline = compile_react_flow_dag(
        valid_graph_payload["nodes"], 
        valid_graph_payload["edges"]
    )
    
    assert pipeline["ticker"] == "XLV"
    assert pipeline["quant_rule"]["indicator"] == "Z_SCORE"
    assert pipeline["quant_rule"]["value"] == -2.0
    assert pipeline["ai_rule"]["prompt"] == "Check macro."

def test_compile_missing_asset_trigger(valid_graph_payload):
    # Remove the asset node
    valid_graph_payload["nodes"].pop(0)
    
    with pytest.raises(GraphCompilationError, match="Graph must contain an Asset Trigger node."):
        compile_react_flow_dag(valid_graph_payload["nodes"], valid_graph_payload["edges"])

def test_compile_incomplete_pipeline_dead_end(valid_graph_payload):
    # Break the connection to the AI node
    valid_graph_payload["edges"].pop(1)
    
    with pytest.raises(GraphCompilationError, match="Incomplete strategy"):
        compile_react_flow_dag(valid_graph_payload["nodes"], valid_graph_payload["edges"])
