from django.db import models
from django.db.models import JSONField
from feeds.models import Workspace

class TechCharacterSheet(models.Model):
    """
    Transforms a standard professional resume into a real-time 
    video game-style attribute profile based on verified tracking.
    """
    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, primary_key=True)
    
    # Core Character Stats (0.0 to 100.0)
    algorithmic_depth = models.FloatField(default=10.0)      # Discrete math, graph theory, optimization
    systems_architecture = models.FloatField(default=5.0)    # Distributed systems, I/O bottlenecks, compilation
    tooling_fluency = models.FloatField(default=5.0)         # Frameworks, CI/CD, language-specific quirks
    domain_specialization = models.FloatField(default=0.0)   # Machine Learning kernels, Quantitative math, etc.
    
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'edu_character_sheets'


class EducationCurator(models.Model):
    """
    Configures the targets that AI agents crawl and qualitatively evaluate.
    """
    id = models.CharField(primary_key=True, max_length=64)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    
    label = models.CharField(max_length=100) # e.g., "MIT 6.824 Distributed Systems Tracking"
    source_url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=[
        ('ocw', 'OpenCourseWare'),
        ('whitepaper', 'Academic Whitepaper'),
        ('documentation', 'Language/API Docs'),
        ('media', 'YouTube/Tech Media')
    ])
    
    # Specific qualitative guardrails provided by the user. If blank, expanded defaults take over.
    user_focus_directive = models.TextField(null=True, blank=True)
    
    compiled_pipeline = JSONField() # Stores structured metadata for the crawler
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'edu_curator_pipelines'
