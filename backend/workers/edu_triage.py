import ctypes
import math
from celery import shared_task
from django.utils import timezone
from education.models import EducationCurator, TechCharacterSheet
from education.syllabus_factory import expand_educational_intent
from ai.llm_client import FrontierModelClient

# Load Native C++ Educational Core Scanner
KERNEL_LIB_PATH = "kernel/build/libkernel.so"
kernel_lib = ctypes.CDLL(KERNEL_LIB_PATH)
kernel_lib.scan_educational_signal.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
kernel_lib.scan_educational_signal.restype = ctypes.c_bool

@shared_task
def triage_educational_resource(pipeline_id: str, raw_scraped_text: str):
    pipeline = EducationCurator.objects.get(id=pipeline_id)
    char_sheet, _ = TechCharacterSheet.objects.get_or_create(workspace=pipeline.workspace)
    
    # 1. High-Performance C++ Pre-Filter
    encoded_text = raw_scraped_text.encode('utf-8')
    is_high_signal = kernel_lib.scan_educational_signal(encoded_text, len(encoded_text), 3)
    
    if not is_high_signal:
        return {"status": "dropped", "reason": "Low computational concept density"}

    # 2. Intent Expansion Resolution
    resolved_directive = expand_educational_intent(pipeline.resource_type, pipeline.user_focus_directive)

    # 3. Frontier Model Qualitative Synthesis
    llm = FrontierModelClient()
    system_prompt = f"""
    You are an elite systems architect and technical interviewer tracking education signals.
    Analyze the incoming content under this tracking directive: "{resolved_directive}"
    
    Evaluate the structural payload and output a JSON response specifying:
    1. "architectural_takeaway": A concise Notion-style technical note (max 3 bullets).
    2. "primary_stat_domain": One of ["algorithmic_depth", "systems_architecture", "tooling_fluency", "domain_specialization"]
    3. "complexity_weight": A float between 0.1 (trivial syntax) and 1.0 (cutting-edge systems/math concepts).
    """
    
    evaluation = llm.evaluate_education_payload(system_prompt, context=raw_scraped_text)
    
    # 4. Update the Video Game Stats Profile
    stat_to_update = evaluation.get("primary_stat_domain", "tooling_fluency")
    weight = float(evaluation.get("complexity_weight", 0.1))
    
    # Math Graduate Career Transition XP Curve Formulation
    base_xp = 0.45 
    delta_stat = base_xp * weight
    
    # Current value tracking
    current_val = getattr(char_sheet, stat_to_update)
    new_val = min(100.0, current_val + delta_stat) # Cap at level 100
    setattr(char_sheet, stat_to_update, new_val)
    char_sheet.save()
    
    # 5. Dispatch to Notion-style daily workspace feed
    # dispatch_to_notion_feed(workspace=pipeline.workspace, title=pipeline.label, data=evaluation)

    return {
        "status": "processed",
        "stat_boosted": stat_to_update,
        "increment": delta_stat,
        "new_score": new_val
    }
