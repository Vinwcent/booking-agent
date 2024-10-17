from gradio.processing_utils import logging
from datetime import date, datetime

logger = logging.getLogger("booking-agent")

def get_today_date():
    """
    Get today's date in format "A YYYY-m-d"
    """
    logger.debug("Retrieving today's date")
    day = datetime.now().strftime("%A")
    return day + " " + str(date.today())
