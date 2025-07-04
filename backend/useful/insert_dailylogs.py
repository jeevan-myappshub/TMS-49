from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URI
from models.dailylogs import DailyLog
from models.timesheet import Timesheet
from models.dailylogschanges import DailyLogChange
from faker import Faker
import random
from datetime import timedelta, datetime

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# Fetch all timesheets to associate daily logs with them
timesheets = session.query(Timesheet).all()
if not timesheets:
    print("No timesheets found. Please insert timesheets first.")
    exit()

# Helper to get a random time in the day (returns datetime.time)
def random_time(start_hour=8, end_hour=18):
    hour = random.randint(start_hour, end_hour)
    minute = random.choice([0, 15, 30, 45])
    return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

# Insert 200 fake daily logs
for _ in range(200):
    timesheet = random.choice(timesheets)
    log_date = fake.date_between(start_date=timesheet.week_starting, end_date=timesheet.week_starting + timedelta(days=6))
    morning_in = random_time(8, 10)
    morning_out = random_time(11, 12)
    afternoon_in = random_time(13, 14)
    afternoon_out = random_time(16, 18)
    # Calculate total hours as timedelta
    total_seconds = 0
    if morning_in and morning_out:
        total_seconds += (datetime.combine(log_date, morning_out) - datetime.combine(log_date, morning_in)).seconds
    if afternoon_in and afternoon_out:
        total_seconds += (datetime.combine(log_date, afternoon_out) - datetime.combine(log_date, afternoon_in)).seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    total_hours = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()
    description = fake.sentence(nb_words=10)
    day_of_week = log_date.strftime("%A")

    log = DailyLog(
        timesheet_id=timesheet.id,
        log_date=log_date,
        day_of_week=day_of_week,
        morning_in=morning_in,
        morning_out=morning_out,
        afternoon_in=afternoon_in,
        afternoon_out=afternoon_out,
        total_hours=total_hours,
        description=description
    )
    session.add(log)

session.commit()
print("Inserted 200 random daily log records.")

session.close()