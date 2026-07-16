import os
import asyncio
import json
from google.genai import types
from google.genai.errors import ServerError
from schema import CourseSyllabus
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(ServerError),
    before_sleep=lambda retry_state: print(f"⚠️ Server busy. Retrying in {retry_state.next_action.sleep} seconds...")
)
def call_gemini_with_retry(prompt: str) -> any:
    """Wrapper to safely execute the API call with structural schemas."""
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CourseSyllabus.model_json_schema(), 
            temperature=0.2,
        ),
    )

# 1. Turned this function ASYNC to match Day 3 Orchestrator
async def syllabus_generator_agent(shared_state: dict) -> dict:
    """Takes a topic and generates a reliable, schema-aligned syllabus."""
    user_topic = shared_state.get("topic", "General Computer Science")
    prompt = f"Create a comprehensive, logical technical learning path and course syllabus for: {user_topic}."
    
    print(f"🤖 [Syllabus Agent] Generating schema-aligned outline for '{user_topic}'...")
    
    # Run the synchronous API call wrapper in a thread pool so it doesn't block the event loop
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, call_gemini_with_retry, prompt)
    
    data = response.parsed

    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif isinstance(data, str) or data is None:
        data = json.loads(response.text)

    audience = data.get("target_audience", "Intermediate")
    topic = data.get("topic", user_topic)
    chapters = data.get("chapters", [])

    return {
        "course_metadata": {
            "audience": audience,
            "topic": topic
        },
        "chapters_to_write": chapters
    }

# 2. Add the Async Chapter Writer Agent task
async def chapter_writer_agent(shared_state: dict) -> dict:
    """Simulates or calls Gemini to concurrently generate full text markdown for a chapter."""
    chapter_info = shared_state.get("current_processing_node", {})
    title = chapter_info.get("title", "Unknown Chapter")
    summary = chapter_info.get("summary", "")
    
    print(f"✍️ [Writer Agent] Deep-diving into parallel generation for: {title}...")
    
    # Simulate a network generation delay for the chapter text
    await asyncio.sleep(2.5) 
    
    # Return the generated content mapped to a unique key in global state
    return {
        f"content_{title.replace(' ', '_')}": f"# {title}\n\n{summary}\n\n[Full Deep Dive technical content generated here...]"
    }