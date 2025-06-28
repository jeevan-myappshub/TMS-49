from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy.sql import func

class DailyLogChange(Base):
    __tablename__ = 'daily_log_changes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    daily_log_id = Column(Integer, ForeignKey('daily_logs.id'), nullable=False)
    new_description = Column(Text, nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())

    daily_log = relationship('DailyLog', backref='changes')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}