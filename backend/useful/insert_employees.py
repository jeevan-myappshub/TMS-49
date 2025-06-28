from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URI
from models.employee import Employee
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
    # Assign a random manager from already created employees (except for the first employee)
    manager_id = random.choice([emp.id for emp in employees]) if employees else None
    emp = Employee(
        employee_name=employee_name,
        email=email,
        manager_id=manager_id
    )
    session.add(emp)
    session.flush()  # Get the id of the newly added employee
    employees.append(emp)

session.commit()
print("Inserted 50 random employee records with managers.")

session.close()