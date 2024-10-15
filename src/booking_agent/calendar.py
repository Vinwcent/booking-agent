from datetime import date, datetime
from typing import Dict, List
from pydantic import BaseModel, RootModel

class TimeSlot(BaseModel):
    start: str
    end: str
    available: bool


class Calendar(RootModel):
    root: Dict[str, List[TimeSlot]]

    def get_dates(self) -> List[date]:
        dates = []
        for date_str in self.root:
            dates.append(datetime.strptime(date_str, "%Y-%m-%d").date())
        return dates
