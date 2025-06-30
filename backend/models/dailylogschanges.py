from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy.sql import func

# -----------------------------
# DailyLogChange Table
# -----------------------------
class DailyLogChange(Base):
    __tablename__ = 'daily_log_changes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    daily_log_id = Column(Integer, ForeignKey('daily_logs.id', ondelete="CASCADE"), nullable=False)
    new_description = Column(Text, nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship to DailyLog
    daily_log = relationship('DailyLog', back_populates='changes')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}