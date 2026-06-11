import operator
from celery import shared_task
from finance.models import HybridStrategy
from finance.data_feeds import get_price_data, get_recent_news
from ai.llm_client import FrontierModelClient
from kernel.client import NativeQuantEngine

# Inside process_active_strategy():
if quant['indicator'] == 'Z_SCORE':
    # Now evaluating 16 prices per clock cycle in C++ before returning the boolean
    current_metric = NativeQuantEngine.calculate_z_score(prices)

# Map string operators from the JSON payload to actual Python math operations
OPERATOR_MAP = {
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '==': operator.eq
}

@shared_task
def process_active_strategy(strategy_id: str):
    strategy = HybridStrategy.objects.get(id=strategy_id)
    pipeline = strategy.execution_pipeline
    
    ticker = pipeline['ticker']
    quant = pipeline['quant_rule']
    ai = pipeline['ai_rule']
    
    # ---------------------------------------------------------
    # PHASE 1: Dynamic Quantitative Math
    # ---------------------------------------------------------
    prices = get_price_data(ticker, window_days=20)
    
    # Dynamically select the math routing based on the visual node
    if quant['indicator'] == 'Z_SCORE':
        current_metric = calculate_z_score(prices)
    else:
        # Fallback/Placeholder for RSI, MACD, etc.
        current_metric = 0.0 
        
    # Evaluate the threshold using Python's operator module mapping
    # e.g., operator.lt(current_z_score, -2.0)
    compare_func = OPERATOR_MAP.get(quant['operator'], operator.lt)
    
    if not compare_func(current_metric, quant['value']):
        return {"status": "quant_failed"}

    # ---------------------------------------------------------
    # PHASE 2: AI Contextualization (Triggered)
    # ---------------------------------------------------------
    market_context = get_recent_news(ticker, hours=24)
    llm = FrontierModelClient()
    
    system_directive = f"""
    The asset {ticker} triggered a {quant['indicator']} alert at {current_metric:.2f}.
    Review the market context and answer this directive: "{ai['prompt']}"
    
    Respond strictly in JSON: {{"trigger_alert": boolean, "rationale": "string"}}
    """
    
    decision = llm.evaluate_sentiment(system_directive, context=market_context)
    
    if decision.get("trigger_alert"):
        # Alert the user and update the database timestamp
        strategy.last_triggered_at = timezone.now()
        strategy.save(update_fields=['last_triggered_at'])
        # dispatch_alert(...)
        
    return {"status": "completed", "action_taken": decision.get("trigger_alert")}
