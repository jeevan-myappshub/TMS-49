from sqlalchemy import create_engine
from config.config import SQLALCHEMY_DATABASE_URI
from models.base import Base

# Import all your models so Base knows about them
import models.employee
import models.timesheet
import models.dailylogs
import models.dailylogschanges

engine = create_engine(SQLALCHEMY_DATABASE_URI)

# This will create all tables in the database
Base.metadata.create_all(engine)

print("All tables created successfully!")