import pytest
from workers.tasks import process_inbound_feed

pytestmark = pytest.mark.django_db

class TestIngestionPipeline:

    def test_high_similarity_vectors_are_persisted(self, mock_cpp_kernel, mock_ai_engine):
        """If tau is >= 0.72, the worker should write the entity to the database."""
        
        # Force the mocked AI to return a passing mathematical threshold
        mock_ai_engine.return_value = 0.85
        
        # Execute the Celery task synchronously for testing
        result = process_inbound_feed("https://example.com/rss")
        
        assert mock_cpp_kernel.called
        assert result['status'] == 'persisted'
        assert result['vectors_written'] == 1

    def test_low_similarity_vectors_are_dropped_from_memory(self, mock_cpp_kernel, mock_ai_engine):
        """If tau is < 0.72, the worker should drop the payload to save disk I/O."""
        
        # Force the mocked AI to return a failing mathematical threshold
        mock_ai_engine.return_value = 0.45
        
        # Execute the Celery task
        result = process_inbound_feed("https://example.com/rss")
        
        assert mock_cpp_kernel.called
        assert result['status'] == 'dropped'
        assert result['vectors_written'] == 0
