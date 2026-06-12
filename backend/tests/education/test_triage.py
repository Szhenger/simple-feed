import pytest
from unittest.mock import patch, MagicMock
from workers.edu_triage import triage_educational_resource
from education.models import EducationCurator, TechCharacterSheet
from feeds.models import Workspace

pytestmark = pytest.mark.django_db(transaction=True)

class TestEduOrchestrator:

    @pytest.fixture
    def setup_environment(self):
        ws = Workspace.objects.create(id="ws_shubert_test", name="Shubert's Desk")
        pipeline = EducationCurator.objects.create(
            id="pipe_1", workspace=ws, label="MIT 6.824", resource_type="ocw",
            user_focus_directive="Focus on consensus algorithms.", compiled_pipeline={}
        )
        # Setup base character sheet
        sheet = TechCharacterSheet.objects.create(
            workspace=ws, systems_architecture=10.0
        )
        return pipeline, sheet

    @patch('workers.edu_triage.NativeEduScanner.extract_high_signal_text')
    @patch('workers.edu_triage.FrontierModelClient.evaluate_education_payload')
    def test_worker_updates_stats_on_high_signal(self, mock_llm, mock_scanner, setup_environment):
        pipeline, sheet = setup_environment
        
        # 1. Mock C++ Kernel returning condensed text
        mock_scanner.return_value = "Raft consensus requires leader election and log replication."
        
        # 2. Mock LLM returning a high-complexity systems payload
        mock_llm.return_value = {
            "architectural_takeaway": ["Raft handles partition tolerance cleanly."],
            "primary_stat_domain": "systems_architecture",
            "complexity_weight": 0.8  # High complexity
        }

        # 3. Execute Celery Task
        result = triage_educational_resource(pipeline.id, "Raw scraped text block...")

        # 4. Assert Pipeline Success
        assert result["status"] == "processed"
        assert result["stat_boosted"] == "systems_architecture"
        
        # 5. Assert Math (Base 0.45 * Weight 0.8 = 0.36 increase)
        sheet.refresh_from_db()
        assert round(sheet.systems_architecture, 2) == 10.36

    @patch('workers.edu_triage.NativeEduScanner.extract_high_signal_text')
    def test_worker_halts_on_low_signal_without_calling_llm(self, mock_scanner, setup_environment):
        pipeline, _ = setup_environment
        
        # C++ Kernel determines the document is fluff and returns empty string
        mock_scanner.return_value = ""

        with patch('workers.edu_triage.FrontierModelClient') as MockLLM:
            result = triage_educational_resource(pipeline.id, "Just some marketing fluff...")
            
            assert result["status"] == "dropped"
            assert "sufficient computational density" in result["reason"]
            MockLLM.assert_not_called() # Crucial: Proves we save money/tokens
