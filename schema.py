from pydantic import BaseModel, Field
from typing import List

class ChapterOutline(BaseModel):
    title: str = Field(description="The clear, concise title of the chapter.")
    summary: str = Field(description="A brief paragraph summarizing what this chapter covers.")

class CourseSyllabus(BaseModel):
    topic: str = Field(description="The primary target subject of the entire course.")
    target_audience: str = Field(description="The expected experience level (e.g., Beginner, Advanced).")
    chapters: List[ChapterOutline] = Field(description="A list of distinct chapters forming the complete course structure.")