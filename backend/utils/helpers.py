from datetime import datetime,timedelta 
import re

def calculate_total_hours(morning_in,morning_out,afternoon_in,afternoon_out):
    """
    calculate the total hours worked in a day given in in and out times 
    all arguments are datetime.time or none 
    returns as timedelta as none.
    """
    total = timedelta()
    if morning_in and morning_out:
        total+=datetime.combine(datetime.today(),morning_out)-datetime.combine(datetime.today(),morning_in)
    if afternoon_in and afternoon_out:
        total+=datetime.combine(datetime.today(),afternoon_out)-datetime.combine(datetime.today(),afternoon_in)
    return total if total!=timedelta() else None

def format_timedelta_to_time(td):
    """
    format a timedelta to time string in HH:MM format
    """
    if td is None:
        return None
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"

def is_valid_email(email):
    """Check if the email is valid using regex.
    """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return bool(re.match(pattern, email))

def get_day_of_week(date_obj):
    """Return the day of the week for a given date object (e.g., 'Monday').
    """
    return date_obj.strftime('%A')


def sanitize_description(desc, max_length=1000):
    """Trim and clean up a description string."""
    if desc is None:
        return ""
    desc = desc.strip()
    return desc[:max_length]

def format_datetime(dt):
    """Format a datetime object as ISO string, or return None."""
    if dt is None:
        return None
    return dt.isoformat()