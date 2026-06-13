import json
import logging
import httpx
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class GlobalLogisticsClient:
    """Stateless client for querying flight and location data, backed by Redis."""
    
    def __init__(self):
        self.api_key = settings.TRAVEL_API_KEY
        self.client = httpx.Client(timeout=10.0)

    def get_optimal_flight(self, origin: str, dest: str, start_date: str, end_date: str) -> dict:
        """Fetches the lowest fare. Caches the result for 6 hours."""
        cache_key = f"flights:{origin}:{dest}:{start_date}:{end_date}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)

        try:
            # Simulated upstream call to a travel aggregator
            response = self.client.get(
                "https://api.travel-aggregator.com/v1/fares",
                params={"origin": origin, "dest": dest, "date_from": start_date, "date_to": end_date},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract cheapest flight
            cheapest = sorted(data.get("itineraries", []), key=lambda x: x["price"])[0]
            
            if cheapest:
                cache.set(cache_key, json.dumps(cheapest), timeout=21600) # 6 hours
                
            return cheapest
        except Exception as e:
            logger.error(f"Flight API failure: {str(e)}")
            return None

    def get_destination_context(self, dest: str) -> str:
        """Fetches current headlines, weather, and exchange rates for the destination."""
        # Simplified for brevity: assumes a composite API call
        return "Current Exchange: 1 USD = 150 JPY. Weather forecast: Mild, approaching autumn. News: Upcoming Golden Week."
