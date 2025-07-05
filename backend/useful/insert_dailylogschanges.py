from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import SQLALCHEMY_DATABASE_URI
from models.dailylogschanges import DailyLogChange
from models.dailylogs import DailyLog
from models.timesheet import Timesheet
from models.employee import Employee  # <-- Corrected import
from faker import Faker
import random

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# Fetch all daily logs to associate changes with them
daily_logs = session.query(DailyLog).all()
if not daily_logs:
    print("No daily logs found. Please insert daily logs first.")
    exit()

# Insert 100 fake daily log changes
for _ in range(100):
    daily_log = random.choice(daily_logs)
    new_description = fake.sentence(nb_words=8)
    change = DailyLogChange(
        daily_log_id=daily_log.id,
        new_description=new_description
    )
    session.add(change)

session.commit()
print("Inserted 100 random daily log change records.")

session.close()