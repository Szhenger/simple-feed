import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_cpp_kernel(mocker):
    """
    Globally intercepts the FFI gRPC client.
    Prevents standard Python tests from attempting to access hardware registers.
    """
    mock_client = mocker.patch('kernel.client.AvxScannerClient.parse_payload')
    
    # Return a deterministic, mocked Protobuf response
    mock_client.return_value = [
        {"title": "Mocked Vector Payload", "content": "Parsed safely without C++.", "pub_date": "2026-06-10"}
    ]
    return mock_client

@pytest.fixture
def mock_ai_engine(mocker):
    """
    Mocks the 768-dimensional sentence-transformer singleton to prevent 
    massive memory allocations during simple unit tests.
    """
    mock_engine = mocker.patch('ai.engine.TransformerSingleton.calculate_similarity')
    return mock_engine
