import asyncio
import time
import json
from orchestrator import AgentNode, WorkflowDAG
from agent_tasks import syllabus_generator_agent, chapter_writer_agent

async def main():
    dag = WorkflowDAG()
    
    # 1. Live Dynamic Input
    print("="*50)
    user_topic = input("🎯 Enter the technical topic you want to generate a course for: ")
    print("="*50 + "\n")
    
    initial_context = {"topic": user_topic}
    
    # Register the foundational syllabus gen node
    dag.add_node(AgentNode("Syllabus_Gen", syllabus_generator_agent))
    
    print("🚀 Starting Asynchronous Orchestration Pipeline...\n")
    start_time = time.time()
    
    # 2. Execute the syllabus agent first
    interim_state = await syllabus_generator_agent(initial_context)
    initial_context.update(interim_state)
    
    chapters = initial_context.get("chapters_to_write", [])
    
    # 3. 🛑 HUMAN-IN-THE-LOOP GATEWAY
    print("\n🛑 [HITL GATEWAY] Reviewing generated syllabus structures...")
    print(f"📋 Course Topic: {initial_context['course_metadata']['topic']}")
    print(f"👥 Target Audience: {initial_context['course_metadata']['audience']}")
    print(f"📚 Total Chapters Proposed: {len(chapters)}")
    for idx, ch in enumerate(chapters):
        print(f"   {idx+1}. {ch.get('title')}")
        
    print("\n" + "-"*30)
    user_decision = input("🤔 Review the outline above. Proceed to parallel chapter drafting? (yes/no): ").strip().lower()
    print("-"*30 + "\n")
    
    if user_decision != "yes":
        print("❌ Pipeline execution aborted by the user. Exiting safely.")
        return

    print("✅ Outline Approved! Spawning concurrent worker branches...\n")

    # 4. Dynamic Branching based on verified chapters
    for idx, ch in enumerate(chapters):
        node_id = f"Writer_Chapter_{idx+1}"
        
        async def make_writer_task(state, ch_data=ch):
            state_copy = dict(state)
            state_copy["current_processing_node"] = ch_data
            return await chapter_writer_agent(state_copy)
            
        dag.add_node(AgentNode(node_id, make_writer_task))
        dag.add_dependency("Syllabus_Gen", node_id)
        
    # 5. Fire parallel execution layers concurrently
    final_output = await dag.run(initial_context)
    end_time = time.time()
    
    print("\n" + "="*50)
    print(f"⚡ Parallel Pipeline Run Completed in: {end_time - start_time:.2f} seconds!")
    print(f"🎉 Fully Automated System Complete!")

if __name__ == "__main__":
    asyncio.run(main())