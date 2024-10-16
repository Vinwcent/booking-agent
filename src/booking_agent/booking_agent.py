import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import StructuredTool
from booking_agent.booking_tools import get_today_date
from booking_agent.calendar_toolkit import CalendarToolkit
from booking_agent.memory_tools_agent import MemoryToolsAgent

logger = logging.getLogger("booking-agent")

class BookingAgent(MemoryToolsAgent):
    _calendar_toolkit: CalendarToolkit

    def __init__(self, model: BaseChatModel, calendar_toolkit: CalendarToolkit):
        self._calendar_toolkit = calendar_toolkit
        super().__init__(model, [
            StructuredTool.from_function(get_today_date),
            StructuredTool.from_function(self._calendar_toolkit.is_time_slot_available),
            StructuredTool.from_function(self._calendar_toolkit.book),
            StructuredTool.from_function(self._calendar_toolkit.get_available_slots)
        ], """You are a booking assistant that tries to help people
        booking appointments in their calendar. If there's an availability
        issue you take initiative to suggest direct concrete workaround for the user (check for
        workarounds and propose handy solutions) without asking user if you
        should do it. You understand that people are often considering today's
                         date by default except when they specifically precised
                         a date. You know that when people speak about next
                         week, they speak about the week starting at the next Monday.""")

    def reset_agent_and_calendar(self, calendar_toolkit: CalendarToolkit):
        self._calendar_toolkit = calendar_toolkit
        self._reset_memory_and_rebind_tools([
            StructuredTool.from_function(get_today_date),
            StructuredTool.from_function(self._calendar_toolkit.is_time_slot_available),
            StructuredTool.from_function(self._calendar_toolkit.book),
            StructuredTool.from_function(self._calendar_toolkit.get_available_slots)
        ])

    def get_calendar_json(self):
        return self._calendar_toolkit.get_calendar_json()
