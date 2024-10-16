from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, RootModel

def get_time_obj(time_str: str):
    return datetime.strptime(time_str, "%H:%M")

def get_in_minutes(time: str) -> int:
    time_obj = get_time_obj(time)
    return time_obj.hour * 60 + time_obj.minute

class TimeSlot(BaseModel):
    start: str
    end: str
    available: bool

    def get_duration_in_minutes(self):
        return get_in_minutes(self.end) - get_in_minutes(self.start)



class Calendar(RootModel):
    root: Dict[str, List[TimeSlot]]
