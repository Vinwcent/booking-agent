from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, RootModel

def get_time_obj(time_str: str):
    """
    Transforms a time str in format H:M to a time object

    :param time_str: The time str to be transformed
    """
    return datetime.strptime(time_str, "%H:%M")

def get_in_minutes(time: str) -> int:
    """
    Converts a time str in H:M format to an int that is the amount of minutes it
    represents

    :param time: The time str in H:M format
    :return: The amount of minutes
    """
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
