from sqlalchemy import Column, Integer, Date, String, Time, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base
from models.dailylogschanges import DailyLogChange  # <-- Add this line

class DailyLog(Base):
    __tablename__ = 'daily_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timesheet_id = Column(Integer, ForeignKey('timesheets.id', ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)
    day_of_week = Column(String(10))
    morning_in = Column(Time)
    morning_out = Column(Time)
    afternoon_in = Column(Time)
    afternoon_out = Column(Time)
    total_hours = Column(Time)
    description = Column(Text)

    # Relationship to Timesheet
    timesheet = relationship('Timesheet', back_populates='daily_logs')

    # Relationship to DailyLogChange
    changes = relationship(
        'DailyLogChange',
        back_populates='daily_log',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def as_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Convert time and date objects to string
            if hasattr(value, 'isoformat'):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result