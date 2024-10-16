from typing import Dict, List
from pydantic import BaseModel, RootModel

class TimeSlot(BaseModel):
    start: str
    end: str
    available: bool


class Calendar(RootModel):
    root: Dict[str, List[TimeSlot]]
