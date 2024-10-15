import json
from booking_agent.calendar import Calendar



class TestCalendar:

    def test_creation(self):
        with open("tests/test_files/calendar_test.json", "r") as f:
            json_calendar = json.load(f)
        calendar = Calendar(**json_calendar)
        assert len(calendar.get_dates()) == 3
