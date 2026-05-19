from pydantic import BaseModel

class Facts(BaseModel):
    project_topic: str = ""
    problem: str = ""
    target_audience: str = ""
    goal_hint: str = ""
    expected_result_hint: str = ""
    participants_hint: int | None = None
    educational_program_hint: str = ""
    technologies: list[str] = []
    important_details: list[str] = []
    limitations: list[str] = []

class Application(BaseModel):
    title: str = ""
    goal: str = ""
    result: str = ""
    criteria: list[str] = []
    description: str = ""
    max_participants: int = 5
    educational_program: str = ""
