import asyncio
from collections import defaultdict, deque
from typing import List, Callable, Dict, Any, Awaitable

class AgentNode:
    """Represents an asynchronous AI Agent task in our graph execution tree."""
    def __init__(self, name: str, agent_function: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        self.name = name
        self.agent_function = agent_function  

    async def execute(self, shared_state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"🚀 Running Agent: {self.name}")
        return await self.agent_function(shared_state)


class WorkflowDAG:
    """Manages agent execution concurrently using asynchronous topological layers."""
    def __init__(self):
        self.nodes: Dict[str, AgentNode] = {}
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)

    def add_node(self, node: AgentNode):
        self.nodes[node.name] = node
        if node.name not in self.in_degree:
            self.in_degree[node.name] = 0

    def add_dependency(self, from_node: str, to_node: str):
        self.adjacency_list[from_node].append(to_node)
        self.in_degree[to_node] += 1

    def get_execution_layers(self) -> List[List[str]]:
        """
        Groups independent nodes into parallel execution layers.
        All nodes within a single layer can be executed concurrently.
        """
        local_in_degree = dict(self.in_degree)
        queue = deque([node for node in self.nodes if local_in_degree[node] == 0])
        layers = []

        while queue:
            layer_size = len(queue)
            current_layer = []
            
            for _ in range(layer_size):
                current = queue.popleft()
                current_layer.append(current)

                for neighbor in self.adjacency_list[current]:
                    local_in_degree[neighbor] -= 1
                    if local_in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            layers.append(current_layer)

        if sum(len(layer) for layer in layers) != len(self.nodes):
            raise ValueError("❌ Cyclic dependency detected in agent architecture!")

        return layers

    async def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Executes layers concurrently using asyncio.gather."""
        layers = self.get_execution_layers()
        
        printable_plan = " -> ".join([f"[{', '.join(layer)}]" for layer in layers])
        print(f"📋 Parallel Execution Plan: {printable_plan}\n" + "—"*50)
        
        shared_state = initial_state
        
        for layer in layers:
            # 1. Gather tasks to schedule them inside the asyncio loop
            tasks = [self.nodes[node_name].execute(shared_state) for node_name in layer]
            
            # 2. Await them properly so they resolve to native dict structures, not coroutines
            results = await asyncio.gather(*tasks)
            
            # 3. Safely update the global shared state with the concurrent outcomes
            for result in results:
                if result and isinstance(result, dict):
                    shared_state.update(result)
                    
        return shared_state