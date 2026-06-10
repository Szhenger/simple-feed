import pytest
from django.conf import settings

@pytest.fixture(scope='session', autouse=True)
def configure_integration_settings():
    """
    Forces Celery to run tasks eagerly (synchronously inline) 
    while preserving the full middleware and signal propagation layers.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    
    # Ensure our safety threshold constant is strictly fixed for predictable matching
    settings.AI_TRIAGE_THRESHOLD = 0.72
