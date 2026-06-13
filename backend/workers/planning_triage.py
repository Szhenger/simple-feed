from celery import shared_task
from planning.models import EventManifest, LogisticsSnapshot
from planning.travel_client import GlobalLogisticsClient
from ai.llm_client import FrontierModelClient

@shared_task
def triage_life_events():
    """Iterates through active manifests and triggers reports if conditions are met."""
    active_manifests = EventManifest.objects.filter(is_active=True)
    travel_api = GlobalLogisticsClient()
    llm = FrontierModelClient()
    
    for manifest in active_manifests:
        # 1. Deterministic Check: Get Flights
        flight = travel_api.get_optimal_flight(
            manifest.origin_code, manifest.destination_code, 
            str(manifest.target_date_start), str(manifest.target_date_end)
        )
        
        if not flight:
            continue
            
        current_price = float(flight["price"])
        
        # 2. Gatekeeper: Only proceed if price is within PM's budget
        if current_price > manifest.max_flight_price_usd:
            continue
            
        # 3. Assemble Context for AI
        local_context = travel_api.get_destination_context(manifest.destination_code)
        
        system_prompt = f"""
        You are an executive assistant reporting to a Project Manager. 
        Analyze this local data: {local_context}
        Execute this directive exactly: "{manifest.ai_reporting_directive}"
        
        Write a concise, Notion-style markdown brief. Use bullet points. 
        Focus strictly on actionable logistics, weather risks, and exchange rate impact.
        """
        
        # 4. Generate Qualitative Report
        ai_brief = llm.generate_brief(system_prompt)
        
        # 5. Save the Snapshot (which the React UI will instantly pick up)
        LogisticsSnapshot.objects.create(
            manifest=manifest,
            lowest_fare_found=current_price,
            fare_metadata=flight,
            ai_synthesized_brief=ai_brief,
            trigger_condition_met=True
        )
