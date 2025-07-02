from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URI
from models.employee import Employee
from models.timesheet import Timesheet
from models.dailylogs import DailyLog
from models.dailylogschanges import DailyLogChange
from models.base import Base
from faker import Faker
import random

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# Insert 50 employees
employees = []
for i in range(1, 51):
    employee_name = fake.name()
    email = fake.unique.email()
    reports_to = random.choice([emp.id for emp in employees]) if employees else None
    emp = Employee(
        employee_name=employee_name,
        email=email,
        reports_to=reports_to
    )
    session.add(emp)
    session.flush()
    employees.append(emp)

session.commit()
print("Inserted 50 random employee records with hierarchy (reports_to).")

session.close()