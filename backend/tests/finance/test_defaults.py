import pytest
from finance.market_defaults import resolve_market_intent, AssetClass, DEFAULT_AGENTIC_PROMPTS

def test_intent_expansion_empty_prompt_crypto():
    # BTC should trigger the Crypto heuristic when no prompt is provided
    resolved = resolve_market_intent("BTC", "")
    assert resolved == DEFAULT_AGENTIC_PROMPTS[AssetClass.CRYPTO]
    assert "smart contract vulnerability" in resolved

def test_intent_expansion_short_prompt_forex():
    # Too short of a prompt (<15 chars) should be overwritten/expanded
    resolved = resolve_market_intent("EURUSD", "why down?")
    assert resolved == DEFAULT_AGENTIC_PROMPTS[AssetClass.FOREX]
    assert "central bank interest rate" in resolved

def test_intent_expansion_valid_prompt_combination():
    # A fully specified prompt should append the guardrails, not overwrite
    user_prompt = "Check if the recent earnings call mentioned AI infrastructure spending."
    resolved = resolve_market_intent("NVDA", user_prompt)
    
    # NVDA is not in TICKER_MAP, so it defaults to EQUITY
    assert resolved.startswith(user_prompt)
    assert "Additionally, evaluate these foundational guardrails:" in resolved
    assert "structural breakdown in corporate fundamentals" in resolved
