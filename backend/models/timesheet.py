from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from models.base import Base
from models.employee import Employee  # Ensure this import exists

class Timesheet(Base):
    __tablename__ = 'timesheets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    week_starting = Column(Date, nullable=False)

    employee = relationship('Employee', backref='timesheets')

    def as_dict(self):
        """Convert ORM object to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}