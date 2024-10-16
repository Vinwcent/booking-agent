import logging
from typing import List, Optional, Tuple, cast

from booking_agent.calendar import Calendar, TimeSlot, get_in_minutes
from booking_agent.exceptions import DateUnavailableError, TimeSlotUnavailableError


date_error_msg = "The calendar doesn't provide information about this specific date."


logger = logging.getLogger("booking-agent")

class CalendarToolkit:
    """
    A class designed to abstract the concept of what is a calendar.
    For simplicity here, I directly access the calendar object but in production,
    this would be an abstract class and a strategy design pattern could be
    implemented to adapt to the client calendar (google calendar, apple calendar..)
    """
    _calendar: Calendar

    def __init__(self, calendar: Calendar):
        self._calendar = calendar

    ############
    #  Public  #
    ############

    def get_calendar_json(self):
        """
        Get the current loaded calendar in json format
        """
        return self._calendar.model_dump()

    def book(self, date: str, start_time: str, duration: str):
        """
        Book on specified time slot with an appointment.

        :param date: The date in format YYYY-m-d at which we want to check availability
        :param start_time: The start time of the slot in format HH:mm
        :param duration: The duration of the slot in format HH:mm
        """
        logger.debug(f"Booking on {date} at {start_time} for a duration of {duration}")
        if not self.is_time_slot_available(date, start_time, duration):
            return "This time slot is not available for booking or the duration is not fitting in this specific time slot."
        try:
            slot = self._find_slot(date, start_time)
        except DateUnavailableError:
            return date_error_msg
        except TimeSlotUnavailableError:
            return f"The calendar doesn't provide information about the slot you asked on {date}"
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
            return f"The calendar doesn't provide information about the slot you asked on {date}"
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
            slots_rec = self._get_available_slots_rec(date, duration)
        except DateUnavailableError:
            return date_error_msg
        if slots_rec is None:
            return f"No available slots for {duration}"

        slots_pack, multiplier = slots_rec
        if multiplier == 1:
            logger.debug(f"Found the following slots {slots_pack}, with multiplier {multiplier}")
            slots_str = ", ".join([f"{slot.start} up to {slot.end}" for slot in slots_pack])
            return f"On date {date}, available slots are {slots_str}"

        slots_str = ""
        slots_pack = cast(List[List[TimeSlot]], slots_pack) # For pyright
        for pack_number, pack in enumerate(slots_pack):
            slots_str += f"Combination {pack_number}:\n"
            for slot in pack:
                slots_str += f"{slot.start} up to {slot.end}"

        return f"On date {date}, there's no single slot of that duration. Here are combinations that would simulate this duration when they are booked {slots_str}!."

    #############
    #  Private  #
    #############

    def _get_available_slots_rec(self, date: str, duration: str, rec_multiplier = 1) -> Optional[Tuple[List[TimeSlot], int]]:
        """
        Hacky function that get the available slots that fit a duration at a
        specific date.
        If there's no available slots, it tries recursively with
        half the duration and increase a rec_multiplier until it finds available slots,
        then it groups them to make contiguous groups that could simulate the
        duration wanted.
        """
        logger.debug(f"Getting available slots on {date} for {duration}")
        slots = self._get_slots(date)
        filtered_slots = [slot for slot in slots if slot.available and self._is_duration_valid(slot, duration)]
        logger.debug(f"Found the following slots: {filtered_slots}")
        duration_in_minutes = get_in_minutes(duration)

        # No slots available
        if len(filtered_slots) == 0:
            # We go out if we splitted too much (30 is half the minimum amount
            # here, in reality this would be to define according to the calendar
            # type)
            if duration_in_minutes < 30:
                return None
            half_minutes = duration_in_minutes / 2
            hours, minutes = divmod(half_minutes, 60)
            half_duration = f"{int(hours):02d}:{int(minutes):02d}"
            # Try with half the duration and increase the multiplier
            return self._get_available_slots_rec(date, half_duration, rec_multiplier + 1)
        # Slots available and it was straightforward, we simply return them
        if rec_multiplier == 1:
            return filtered_slots, rec_multiplier

        # We trim and group the slots found to match the total duration wanted
        total_duration = duration_in_minutes * 2 ** (rec_multiplier - 1)
        groups = self._trim_and_group_slots(total_duration, filtered_slots)
        # Maybe we can't if we're in a case where available slots are surrounded
        # by unavailable ones
        if len(groups) == 0:
            return None
        return groups, rec_multiplier


    def _trim_and_group_slots(self, duration_wanted_m: int, slots: List[TimeSlot]):
        """
        Goes through the slots and group them to create groups of contiguous
        slots that could simulate the duration wanted

        :param duration_wanted_m: The duration wanted in minutes
        :param slots: All the available slots we want to trim
        """
        if len(slots) == 0:
            return slots
        groups = []
        running_duration = slots[0].get_duration_in_minutes()
        running_slots = [slots[0]]
        for index in range(1, len(slots)):
            slot = slots[index]
            last_end = running_slots[-1].end
            if slot.start == last_end:
                running_duration += slot.get_duration_in_minutes()
                running_slots.append(slot)
                if running_duration >= duration_wanted_m:
                    groups.append(running_slots)
                    running_slots = [slot]
                    running_duration = slot.get_duration_in_minutes()
                continue
            # Here we finished a group that can't simulate the duration wanted
            running_slots = [slot]
            running_duration = slot.get_duration_in_minutes()
        return groups

    def _get_slots(self, date: str) -> List[TimeSlot]:
        """
        Get all the slots at a specified date in YYYY-m-d format

        :param date: The date in YYYY-m-d format
        :return: The list of time slots at this date
        :raises DateUnavailableError: date not found in calendar
        """
        calendar_dict = self._calendar.root
        if date not in calendar_dict.keys():
            raise DateUnavailableError
        return calendar_dict[date]


    def _find_slot(self, date: str, start_time: str) -> TimeSlot:
        """
        Find the slot that begins at start_time on date

        :return: The TimeSlot
        :raises TimeSlotUnavailableError: time slot not found on this day
        """
        slots = self._get_slots(date)

        for slot in slots:
            if slot.start == start_time:
                return slot
        raise TimeSlotUnavailableError

    def _is_duration_valid(self, slot: TimeSlot, duration: str) -> bool:
        """
        Returns a boolean assessing if there's enough time in the given slot for
        the provided duration

        :param slot: The slot to check
        :param duration: The duration is H:M format
        """
        duration_minutes = get_in_minutes(duration)
        available_minutes = slot.get_duration_in_minutes()

        return available_minutes >= duration_minutes

