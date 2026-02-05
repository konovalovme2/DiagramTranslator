import numpy as np

def match_arrows_to_blocks(blocks, arrows):
    graph = {i: [] for i in range(len(blocks))}
    
    for arrow in arrows:
        start = arrow["start"] if "start" in arrow else arrow["center"]
        end = arrow["end"] if "end" in arrow else arrow["center"]
        
        source_idx = min(
            range(len(blocks)),
            key=lambda i: distance(start, blocks[i]["center"])
        )
        target_idx = min(
            range(len(blocks)),
            key=lambda i: distance(end, blocks[i]["center"])
        )
        
        if source_idx != target_idx:
            graph[source_idx].append(target_idx)
    
    return graph

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def translate_graph(graph, blocks, start_idx=0):
    visited = set()
    result = []
    
    def dfs(node_idx, current_indent):
        if node_idx >= len(blocks) or node_idx < 0:
            result.append(" " * current_indent + f"Ошибка: блок {node_idx} не существует")
            return
        
        if node_idx in visited:
            result.append(" " * current_indent + f"ЦИКЛ: возврат к '{blocks[node_idx]['text']}'")
            return
        
        visited.add(node_idx)
        text = blocks[node_idx]["text"].strip()
        result.append(" " * current_indent + text)
        
        neighbors = graph.get(node_idx, [])
        for neighbor_idx in neighbors:
            dfs(neighbor_idx, current_indent)
    
    if start_idx >= len(blocks) or start_idx < 0:
        return [f"Ошибка: стартовый блок {start_idx} не существует"]
    
    dfs(start_idx, 0)
    return result