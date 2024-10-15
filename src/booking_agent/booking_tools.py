from langchain.agents import tool
from datetime import date




@tool
def get_today_date():
    """
    Get today's date
    """
    return date.today()
