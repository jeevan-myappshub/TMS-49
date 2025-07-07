from sqlalchemy import create_engine
import datetime
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URI
from models.timesheet import Timesheet
from models.employee import Employee
from models.dailylogs import DailyLog           # <-- Add this import
from models.dailylogschanges import DailyLogChange  # <-- Add this import
from faker import Faker
import random

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# Fetch all employees to associate timesheets with them
employees = session.query(Employee).all()
if not employees:
    print("No employees found. Please insert employees first.")
    exit()

# Insert 100 fake timesheets
# Insert 50 fake timesheets
for _ in range(50):
    employee = random.choice(employees)
    random_date = fake.date_between(start_date="-1y", end_date="today")
    week_starting = random_date - datetime.timedelta(days=random_date.weekday())
    # Check for existing timesheet for this employee and week
    exists = session.query(Timesheet).filter_by(
        employee_id=employee.id,
        week_starting=week_starting
    ).first()
    if exists:
        continue  # Skip duplicates
    timesheet = Timesheet(
        employee_id=employee.id,
        week_starting=week_starting
    )
    session.add(timesheet)

session.commit()
print("Inserted 50 random timesheet records.")

session.close()