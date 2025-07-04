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

def safe_close(session):
    try:
        session.close()
    except:
        pass

def calculate_total_hours(time_in_am, time_out_am, time_in_pm, time_out_pm):
    total_seconds = 0
    try:
        if time_in_am and time_out_am:
            in_am = datetime.strptime(time_in_am, '%H:%M')
            out_am = datetime.strptime(time_out_am, '%H:%M')
            total_seconds += (out_am - in_am).seconds
        if time_in_pm and time_out_pm:
            in_pm = datetime.strptime(time_in_pm, '%H:%M')
            out_pm = datetime.strptime(time_out_pm, '%H:%M')
            total_seconds += (out_pm - in_pm).seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}:{minutes:02d}"
    except ValueError:
        return "0:00"
