class GraphCompilationError(Exception):
    pass

def compile_react_flow_dag(nodes: list, edges: list) -> dict:
    """
    Traverses the frontend nodes and edges to extract a strict operational pipeline.
    Expects a linear path: Asset -> Quant -> AI.
    """
    pipeline = {}
    
    # 1. Identify nodes by type using a quick lookup dictionary
    node_map = {n['id']: n for n in nodes}
    
    # 2. Find the root trigger (Asset Node)
    asset_nodes = [n for n in nodes if n['type'] == 'asset']
    if not asset_nodes:
        raise GraphCompilationError("Graph must contain an Asset Trigger node.")
    
    root_node = asset_nodes[0]
    pipeline['ticker'] = root_node['data']['ticker']
    
    # 3. Traverse edges to find the next execution block
    current_node_id = root_node['id']
    
    while True:
        # Find the outgoing edge from the current node
        outgoing_edges = [e for e in edges if e['source'] == current_node_id]
        if not outgoing_edges:
            break # End of the pipeline reached
            
        next_node_id = outgoing_edges[0]['target']
        next_node = node_map[next_node_id]
        
        # 4. Map the logic block to our execution pipeline
        if next_node['type'] == 'quant':
            pipeline['quant_rule'] = {
                'indicator': next_node['data']['indicator'],
                'operator': next_node['data']['operator'],
                'value': float(next_node['data']['value'])
            }
        elif next_node['type'] == 'ai':
            pipeline['ai_rule'] = {
                'prompt': next_node['data']['prompt']
            }
            
        current_node_id = next_node_id

    # Validation: Ensure the pipeline isn't a dead-end
    if 'quant_rule' not in pipeline or 'ai_rule' not in pipeline:
        raise GraphCompilationError("Incomplete strategy: Must connect Asset -> Quant -> AI.")

    return pipeline
