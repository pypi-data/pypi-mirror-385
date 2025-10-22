from typing import List, Optional
from pydantic import BaseModel

class Course(BaseModel):
    id: int
    fullname: str


class Event(BaseModel):
    id: int
    name: str
    timestart: int
    timesort: int
    description: Optional[str] = None
    viewurl: Optional[str] = None
    course: Optional[Course] = None


class CalendarResponse(BaseModel):
    events: List[Event]
