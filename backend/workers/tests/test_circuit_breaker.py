import pytest
import grpc
from unittest.mock import MagicMock
from kernel.client import NativeKernelClient
from workers.exceptions import KernelPanicError

class TestGrpcBoundaryEdgeCases:

    def test_grpc_unavailable_triggers_circuit_breaker(self, mocker):
        """
        If the C++ binary dies, the FFI client must immediately raise a bounded 
        internal error rather than hanging the Celery worker thread indefinitely.
        """
        # Mock the gRPC stub to simulate a hard connection refusal
        mock_stub = mocker.patch('kernel.client.AvxScannerStub')
        mock_stub.return_value.ParsePayload.side_effect = grpc.RpcError("UNAVAILABLE")
        
        client = NativeKernelClient()
        
        # Ensure our custom abstraction traps the C-level socket error cleanly
        with pytest.raises(KernelPanicError) as exc_info:
            client.parse_payload(b"<rss><channel>...</channel></rss>")
            
        assert "Native Kernel Unreachable" in str(exc_info.value)
