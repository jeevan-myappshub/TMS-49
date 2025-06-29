from sqlalchemy import Column, Integer, Date, String, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from models.timesheet import Timesheet  # Ensure this import exists


class DailyLog(Base):
    __tablename__ = 'daily_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timesheet_id = Column(Integer, ForeignKey('timesheets.id'), nullable=False)
    log_date = Column(Date, nullable=False)
    day_of_week = Column(String(10))
    morning_in = Column(Time)
    morning_out = Column(Time)
    afternoon_in = Column(Time)
    afternoon_out = Column(Time)
    total_hours = Column(Time)
    descreption = Column(Text)

    timesheet = relationship('Timesheet', backref='daily_logs')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}