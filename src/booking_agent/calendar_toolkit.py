import logging
from datetime import datetime
from typing import List

from booking_agent.calendar import Calendar, TimeSlot
from booking_agent.exceptions import DateUnavailableError, TimeSlotUnavailableError

def get_time_obj(time_str: str):
    return datetime.strptime(time_str, "%H:%M")

date_error_msg = "No informations can be provided about the specific date you asked, either the date is wrong or the calendar does not give information about that day. Please check what you did"


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

    ############
    #  Public  #
    ############

    def book(self, date: str, start_time: str, duration: str):
        """
        Book on specified time slot with an appointment.

        :param date: The date in format YYYY-m-d at which we want to check availability
        :param start_time: The start time of the slot in format HH:mm
        :param duration: The duration of the slot in format HH:mm
        """
        logger.debug(f"Booking on {date} at {start_time} for a duration of {duration}")
        if not self.is_time_slot_available(date, start_time, duration):
            return "This time slot is not available for booking or the duration is not fitting in this specific time slot. Call this function multiple times with smaller durations if you want to book contiguous slot for higher durations"
        try:
            slot = self._find_slot(date, start_time)
        except DateUnavailableError:
            return date_error_msg
        slot.available = False
        return f"Booked at {start_time} on {date} with success"

    def is_time_slot_available(self, date: str,
                               start_time: str, duration: str = "01:00"):
        """
        Returns a boolean assessing if a time slot is available to book an
        appointment.

        :param date: The date in format YYYY-m-d at which we want to check availability
        :param start_time: The start time of the slot in format HH:mm
        :param duration: The duration of the slot in format HH:mm
        """
        logger.debug(f"Checking availability on {date} at {start_time} for a duration of {duration}")
        try:
            slot = self._find_slot(date, start_time)
        except DateUnavailableError:
            return date_error_msg
        except TimeSlotUnavailableError:
            return f"No informations can be provided about the specific time slot you asked on {date}"
        if not slot.available:
            return False
        return self._is_duration_valid(slot, duration)

    def get_available_slots(self, date: str, duration: str):
        """
        Get the slots available at the specified date and that respects a
        specific duration

        :param date: The date we want to check
        :param duration: The duration of the slots we want to have
        """
        logger.debug(f"Getting available slots on {date} for {duration}")
        try:
            slots = self._get_slots(date)
        except DateUnavailableError:
            return date_error_msg
        filtered_slots = [slot for slot in slots if slot.available and
        self._is_duration_valid(slot, duration)]
        logger.debug(f"Found the following slots: {filtered_slots}")
        if len(filtered_slots) == 0:
            return f"No available slots for {duration} hours today, consider checking with half the duration and book multiple contiguous slots to simulate a {duration} appointment"
        return f"On date {date}, slots are " + ", ".join([slot.start for slot in filtered_slots])

    def get_first_available_slot(self, date: str, start_time: str, duration: str):
        """
        Get the start time (in H:M format) of the first available slot on
        a specific day that starts after the start_time provided and which
        respects the duration given

        :param date: The date at which we want an available slot
        :param start_time: The smallest start time we want
        :param duration: The duration of the time slot we want
        """
        logger.debug(f"Searching an available slot on {date} after {start_time}")
        try:
            slots = self._get_slots(date)
        except DateUnavailableError:
            return date_error_msg
        for slot in slots:
            if start_time > slot.start or not slot.available:
                continue
            if self._is_duration_valid(slot, duration):
                logger.debug(f"Found available slot on {date} at {slot.start}")
                return slot.start
        raise ValueError("no available slot")

    #############
    #  Private  #
    #############

    def _get_slots(self, date: str) -> List[TimeSlot]:
        calendar_dict = self._calendar.root
        if date not in calendar_dict.keys():
            raise DateUnavailableError
        return calendar_dict[date]


    def _find_slot(self, date: str, start_time: str) -> TimeSlot:
        slots = self._get_slots(date)

        for slot in slots:
            if slot.start == start_time:
                return slot
        raise TimeSlotUnavailableError

    def _is_duration_valid(self, slot: TimeSlot, duration: str) -> bool:
        start_time_obj = get_time_obj(slot.start)
        end_time_obj = get_time_obj(slot.end)
        duration_obj = get_time_obj(duration)

        available_minutes = end_time_obj.hour * 60 + end_time_obj.minute - start_time_obj.hour * 60 - start_time_obj.minute
        duration_minutes = duration_obj.hour * 60 + duration_obj.minute
        return available_minutes >= duration_minutes
