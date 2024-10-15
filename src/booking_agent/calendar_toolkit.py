import logging
from datetime import datetime

from booking_agent.calendar import Calendar, TimeSlot

def get_time_obj(time_str: str):
    return datetime.strptime(time_str, "%H:%M")


logger = logging.getLogger("booking-agent")

class CalendarToolkit:
    """
    A class designed to abstract the concept of what is a calendar.
    For simplicity we directly access the calendar object but in production,
    this would be an abstract class and subclasses would implement specific
    calendar tools (google calendar, apple calendar..)
    """
    _calendar: Calendar

    def __init__(self, calendar: Calendar):
        self._calendar = calendar

    def book(self, date: str, start_time: str, duration: str):
        """
        Book an appointment at a specified time slot

        :param date: The date in format YYYY-m-d at which we want to check availability
        :param start_time: The start time of the slot in format HH:mm
        :param duration: The duration of the slot in format HH:mm
        """
        if not self.is_time_slot_available(date, start_time, duration):
            raise ValueError("Tried booking a slot that is not available for the parameters {date}, {start_time}, {duration}")
        slot = self._find_slot(date, start_time)
        slot.available = False

    def is_time_slot_available(self, date: str,
                               start_time: str, duration: str = "01:00"):
        """
        Returns a boolean assessing if a time slot is available for booking an
        appointment.

        :param date: The date in format YYYY-m-d at which we want to check availability
        :param start_time: The start time of the slot in format HH:mm
        :param duration: The duration of the slot in format HH:mm
        """
        logger.info(f"Checking availability on {date} at {start_time} for a duration of {duration}")
        slot = self._find_slot(date, start_time)
        if not slot.available:
            return False
        return self._is_duration_valid(slot, duration)

    def _find_slot(self, date: str, start_time: str) -> TimeSlot:
        calendar_dict = self._calendar.root
        if date not in calendar_dict.keys():
            raise ValueError(f"Date {date} is not in Calendar")
        slots = calendar_dict[date]

        for slot in slots:
            if slot.start == start_time:
                return slot
        raise ValueError(f"No time slot starting at {start_time} in calendar")

    def _is_duration_valid(self, slot: TimeSlot, duration: str) -> bool:
        start_time_obj = get_time_obj(slot.start)
        end_time_obj = get_time_obj(slot.end)
        duration_obj = get_time_obj(duration)

        available_minutes = end_time_obj.hour * 60 + end_time_obj.minute - start_time_obj.hour * 60 - start_time_obj.minute
        duration_minutes = duration_obj.hour * 60 + duration_obj.minute
        return available_minutes >= duration_minutes
