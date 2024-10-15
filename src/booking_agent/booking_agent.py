from datetime import date

from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import StructuredTool
from booking_agent.calendar_toolkit import CalendarToolkit
from booking_agent.memory_tools_agent import MemoryToolsAgent


class BookingAgent(MemoryToolsAgent):
    _calendar_toolkit: CalendarToolkit

    def __init__(self, model: BaseLanguageModel, calendar_toolkit: CalendarToolkit, session_id: str = "0"):
        self._calendar_toolkit = calendar_toolkit
        super().__init__(model, [
            StructuredTool.from_function(self.get_today_date),
            StructuredTool.from_function(self._calendar_toolkit.is_time_slot_available),
            StructuredTool.from_function(self._calendar_toolkit.book)
        ], session_id)

    def get_today_date(self):
        """
        Get today's date
        """
        return date.today()
