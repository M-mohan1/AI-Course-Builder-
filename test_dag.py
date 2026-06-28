from orchestrator import AgentNode, WorkflowDAG

# Define dummy functions representing our future AI behaviors
def generate_syllabus(state):
    print(f"   [Processing topic: {state['topic']}]")
    return {"syllabus": ["Intro to Pointers", "Pointer Arithmetic"]}

def write_lesson_1(state):
    print(f"   [Reading outline: {state['syllabus'][0]}]")
    return {"lesson_1_content": "A pointer stores a memory address."}

def write_lesson_2(state):
    print(f"   [Reading outline: {state['syllabus'][1]}]")
    return {"lesson_2_content": "Adding 1 to an int pointer moves it by 4 bytes."}

def review_course(state):
    print("   [Reviewing lessons for errors...]")
    final_book = f"Course: {state['topic']}\n- {state['lesson_1_content']}\n- {state['lesson_2_content']}"
    return {"final_course": final_book}

# Assemble the workflow
if __name__ == "__main__":
    dag = WorkflowDAG()

    # Create the Agent Nodes
    node_syllabus = AgentNode("Syllabus_Gen", generate_syllabus)
    node_l1 = AgentNode("Lesson_1_Writer", write_lesson_1)
    node_l2 = AgentNode("Lesson_2_Writer", write_lesson_2)
    node_reviewer = AgentNode("Final_Reviewer", review_course)

    # Add nodes to graph
    dag.add_node(node_syllabus)
    dag.add_node(node_l1)
    dag.add_node(node_l2)
    dag.add_node(node_reviewer)

    # Define the execution pipeline
    dag.add_dependency("Syllabus_Gen", "Lesson_1_Writer")
    dag.add_dependency("Syllabus_Gen", "Lesson_2_Writer")
    dag.add_dependency("Lesson_1_Writer", "Final_Reviewer")
    dag.add_dependency("Lesson_2_Writer", "Final_Reviewer")

    # Fire off the initial prompt state!
    initial_context = {"topic": "C++ Pointers"}
    final_output = dag.run(initial_context)
    
    print("\n" + "—"*40 + "\n🎯 Final Compiled Output:")
    print(final_output["final_course"])