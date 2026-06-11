import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HybridStrategy
from .compiler import compile_react_flow_dag, GraphCompilationError

logger = logging.getLogger(__name__)

class DeployStrategyView(APIView):
    def post(self, request):
        workspace_id = request.META.get('HTTP_X_WORKSPACE_ID')
        payload = request.data
        
        graph_id = payload.get('graph_id')
        nodes = payload.get('nodes', [])
        edges = payload.get('connections', [])

        try:
            # 1. Compile the visual graph into a backend-friendly dictionary
            compiled_pipeline = compile_react_flow_dag(nodes, edges)
            
            # 2. Persist the executable strategy
            strategy, created = HybridStrategy.objects.update_or_create(
                id=graph_id,
                workspace_id=workspace_id,
                defaults={
                    'asset_ticker': compiled_pipeline['ticker'],
                    'execution_pipeline': compiled_pipeline,
                    'status': 'active'
                }
            )
            
            logger.info(f"Successfully compiled and deployed strategy {graph_id} for {compiled_pipeline['ticker']}.")
            
            return Response({
                "status": "deployed",
                "strategy_id": strategy.id,
                "pipeline": compiled_pipeline
            }, status=status.HTTP_201_CREATED)

        except GraphCompilationError as e:
            logger.error(f"Failed to compile graph {graph_id}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server configuration error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
