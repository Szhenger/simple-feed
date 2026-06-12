import json
import logging
import httpx
from typing import List, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from django.conf import settings
from django.core.cache import cache  # Configured to our Redis cluster

logger = logging.getLogger(__name__)

class MarketAPIError(Exception):
    """Custom exception for upstream financial API failures."""
    pass

class InstitutionalMarketClient:
    """
    Stateless data ingestion client optimized for Celery workers.
    Aggressively caches highly-requested tickers to prevent 429 Rate Limits.
    """
    
    def __init__(self):
        self.api_key = settings.MARKET_DATA_API_KEY
        self.base_url = "https://data.alpaca.markets/v2"
        # Connection pooling for high-throughput I/O
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"APCA-API-KEY-ID": self.api_key},
            timeout=httpx.Timeout(5.0)
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    def _fetch_from_upstream(self, endpoint: str, params: dict) -> dict:
        """Raw network execution with exponential backoff."""
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_closing_prices(self, ticker: str, limit: int = 16) -> List[float]:
        """
        Retrieves a contiguous array of floats required by the C++ AVX-512 kernel.
        Utilizes Redis to ensure O(1) reads for highly-contested tickers.
        """
        cache_key = f"market:prices:{ticker}:{limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)

        # Cache Miss: Fetch from network
        try:
            raw_data = self._fetch_from_upstream(
                endpoint=f"/stocks/{ticker}/bars",
                params={"timeframe": "1Hour", "limit": limit}
            )
            
            # Extract only the closing prices ('c') and cast to float
            bars = raw_data.get("bars", {})
            prices = [float(bar["c"]) for bar in bars]
            
            # Cache for 60 seconds (1-minute candlestick granularity)
            if prices:
                cache.set(cache_key, json.dumps(prices), timeout=60)
                
            return prices
            
        except MarketAPIError as e:
            logger.error(f"Failed to fetch price data for {ticker}: {str(e)}")
            return []

    def get_recent_news(self, ticker: str, limit: int = 3) -> List[str]:
        """
        Fetches qualitative news headlines required for the AI Intent Fallback Engine.
        """
        cache_key = f"market:news:{ticker}:{limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)

        try:
            raw_data = self._fetch_from_upstream(
                endpoint="/news",
                params={"symbols": ticker, "limit": limit}
            )
            
            # Extract headlines and summaries
            articles = raw_data.get("news", [])
            news_payload = [f"{article['headline']} - {article['summary']}" for article in articles]
            
            # News moves slower than prices; cache for 5 minutes
            if news_payload:
                cache.set(cache_key, json.dumps(news_payload), timeout=300)
                
            return news_payload
            
        except MarketAPIError:
            return ["No recent news available."]
