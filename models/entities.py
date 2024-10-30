from typing import List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Employee:
    id: int
    skills: List[str]
    max_hours: float = 40
    current_task: str = None
    hours_worked: float = 0
    breaks_taken: List[int] = field(default_factory=list)
    schedule: List[int] = field(default_factory=list)

@dataclass
class Task:
    id: int
    required_skill: str
    duration: float
    priority: int = 1
    assigned_to: Employee = None
    start_time: datetime = None
    completion_time: datetime = None