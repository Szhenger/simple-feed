from django.db import models
from django.db.models import JSONField
from feeds.models import Workspace

class HybridStrategy(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    
    # Fast-lookup fields for database indexing
    asset_ticker = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'), 
        ('paused', 'Paused'), 
        ('failed', 'Failed')
    ])
    
    # The compiled logical execution tree extracted from React Flow
    execution_pipeline = JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'finance_hybrid_strategies'
