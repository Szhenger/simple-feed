import logging
from celery import shared_task
from typing import Dict, Any

# Mock internal modules
from finance.data_feeds import get_price_data, get_recent_news
from finance.math import calculate_z_score
from ai.llm_client import FrontierModelClient
from notifications.push import dispatch_alert

logger = logging.getLogger(__name__)

@shared_task
def evaluate_hybrid_strategy(strategy_id: str, asset_ticker: str, ai_prompt: str):
    """
    Executes a two-phase strategy evaluation for a user.
    Phase 1: Deterministic Quantitative Math.
    Phase 2: Qualitative LLM Contextualization.
    """
    logger.info(f"Initiating hybrid evaluation for {asset_ticker}")

    # ---------------------------------------------------------
    # PHASE 1: The Quant Layer (Fast, Deterministic)
    # ---------------------------------------------------------
    prices = get_price_data(asset_ticker, window_days=20)
    current_price = prices[-1]
    
    # Calculate the Z-Score to check for statistical deviations
    z_score = calculate_z_score(prices)
    
    if z_score >= -2.0:
        logger.info(f"Quant criteria not met for {asset_ticker} (Z: {z_score:.2f}). Halting.")
        return {"status": "quant_failed", "z_score": z_score}

    logger.warning(f"Quant boundary breached for {asset_ticker}. Fetching context for AI.")

    # ---------------------------------------------------------
    # PHASE 2: The Qualitative AI Layer (Slower, Contextual)
    # ---------------------------------------------------------
    # Fetch the last 24 hours of news/SEC filings to provide context to the LLM
    market_context = get_recent_news(asset_ticker, hours=24)
    
    llm = FrontierModelClient()
    
    # We construct a strict system prompt to force the LLM to act as an analyst,
    # injecting Brick's specific user-defined rule.
    system_directive = f"""
    You are a quantitative financial analyst. 
    The asset {asset_ticker} has experienced a 2-sigma drop (Z-score: {z_score:.2f}).
    Review the following market context and answer the user's specific query.
    
    User Query: "{ai_prompt}"
    
    Respond strictly in JSON format: {{"trigger_alert": boolean, "rationale": "string"}}
    """
    
    ai_decision = llm.evaluate_sentiment(system_directive, context=market_context)
    
    # ---------------------------------------------------------
    # PHASE 3: Independent Execution Handoff
    # ---------------------------------------------------------
    if ai_decision.get("trigger_alert"):
        message = (
            f"🚨 STRATEGY TRIGGER: {asset_ticker}\n"
            f"Math: Z-Score hit {z_score:.2f}.\n"
            f"AI Analysis: {ai_decision['rationale']}\n"
            f"Action: Ready for your manual review and execution."
        )
        dispatch_alert(user_id="brick_med_student", payload=message)
        return {"status": "alert_dispatched", "rationale": ai_decision['rationale']}
    
    return {"status": "ai_rejected", "rationale": ai_decision['rationale']}
