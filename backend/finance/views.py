from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .compiler import compile_react_flow_dag
from .market_defaults import resolve_market_intent

class DeployStrategyView(APIView):
    def post(self, request):
        workspace_id = request.META.get('HTTP_X_WORKSPACE_ID')
        payload = request.data
        
        try:
            # 1. Parse raw spatial connections from React Flow
            compiled_pipeline = compile_react_flow_dag(payload.get('nodes', []), payload.get('connections', []))
            
            # 2. Intercept and resolve agentic prompt under-specifications
            ticker = compiled_pipeline['ticker']
            raw_user_prompt = compiled_pipeline.get('ai_rule', {}).get('prompt', '')
            
            # The system automatically infers intent based on the target market asset class
            resolved_prompt = resolve_market_intent(ticker, raw_user_prompt)
            compiled_pipeline['ai_rule']['prompt'] = resolved_prompt
            
            # 3. Save fully specified execution DAG to database
            # ... strategy = HybridStrategy.objects.update_or_create(...)
            
            return Response({
                "status": "deployed",
                "resolved_prompt": resolved_prompt
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
