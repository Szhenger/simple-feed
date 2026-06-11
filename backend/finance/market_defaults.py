from enum import Enum

class AssetClass(Enum):
    EQUITY = "equity"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"

# Deterministic mapping of tickers to asset categories
TICKER_MAP = {
    "SPY": AssetClass.EQUITY, "XLV": AssetClass.EQUITY, "AAPL": AssetClass.EQUITY,
    "BTC": AssetClass.CRYPTO, "ETH": AssetClass.CRYPTO,
    "EURUSD": AssetClass.FOREX, "DXY": AssetClass.FOREX,
    "GLD": AssetClass.COMMODITY, "USO": AssetClass.COMMODITY
}

DEFAULT_AGENTIC_PROMPTS = {
    AssetClass.EQUITY: (
        "Identify if the current price deviation is driven by systemic market contagion, "
        "macroeconomic overreaction, or an actual structural breakdown in corporate fundamentals "
        "(such as terminal earnings misses, balance sheet fraud, or senior executive flight)."
    ),
    AssetClass.CRYPTO: (
        "Determine if the current volatility is caused by a protocol-level smart contract vulnerability, "
        "centralized exchange liquidity crisis, or localized regulatory panic. Disregard standard "
        "social media noise and focus purely on chain integrity and developer consensus."
    ),
    AssetClass.FOREX: (
        "Evaluate whether the currency move aligns with unexpected structural changes in central bank interest rate "
        "guidance (e.g., unexpected hawkish/default shifts) or macro data surprises (CPI, unemployment) vs simple interday short-squeezes."
    ),
    AssetClass.COMMODITY: (
        "Analyze whether the price action is a consequence of structural geopolitical supply chain disruptions, "
        "freight logistics collapses, unexpected inventory builds/drawdowns, or standard speculative futures rolling."
    )
}

def resolve_market_intent(ticker: str, user_prompt: str = None) -> str:
    """
    Guarantees the agent always has a high-fidelity operational directive.
    If the user leaves the field empty or too brief, it dynamically injects the institutional standard.
    """
    # Fallback to general equity if ticker unrecognized
    asset_class = TICKER_MAP.get(ticker.upper(), AssetClass.EQUITY)
    
    # If the user prompt is completely empty, missing, or lazily configured (e.g., "tell me what happened")
    if not user_prompt or len(user_prompt.strip()) < 15:
        return DEFAULT_AGENTIC_PROMPTS[asset_class]
        
    # Agentic Expansion: Append the fallback safety net to the user's specific text
    return f"{user_prompt.strip()} Additionally, evaluate these foundational guardrails: {DEFAULT_AGENTIC_PROMPTS[asset_class]}"
