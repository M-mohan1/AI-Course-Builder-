from orchestrator import AgentNode, WorkflowDAG
from agent_tasks import syllabus_generator_agent
import json

if __name__ == "__main__":
    # 1. Initialize our framework graph engine
    dag = WorkflowDAG()
    
    # 2. Register our AI Agent Node
    syllabus_node = AgentNode("Syllabus_Gen", syllabus_generator_agent)
    dag.add_node(syllabus_node)
    
    # 3. Setup initial global memory input
    initial_context = {"topic": "Memory Management and Smart Pointers in C++"}
    
    # 4. Fire the engine execution!
    print("🎬 Starting Day 2 Agent Execution Lifecycle...\n")
    final_state = dag.run(initial_context)
    
    print("\n" + "="*50)
    print("🎯 Global State Modified Safely! Resulting Payload Structure:")
    print(json.dumps(final_state, indent=4))