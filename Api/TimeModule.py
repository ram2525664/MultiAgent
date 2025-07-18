from datetime import datetime
from zoneinfo import ZoneInfo
import pytz

# getting the current time in a specific timezone
def get_time(_: str) -> str:
    """Returns the current time."""
    return datetime.now().strftime("%I:%M %p")

# getting the current date
def get_date(_: str) -> str:
    """Returns today's date."""
    return datetime.now().strftime("%d %B %Y")

# getting the current day of the week
def get_day(_: str) -> str:
    """Returns the current day of the week."""
    return datetime.now().strftime("%A")

# getting the full current date and time
def get_datetime(_: str) -> str:
    """Returns the full current date, time, and day."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

# getting the precise timezone
def get_precise_timezone(_: str) -> str:
    """Returns the full IANA timezone name like Asia/Kolkata."""
    now = datetime.now()
    return now.astimezone().tzinfo.key
