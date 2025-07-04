from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    reports_to = Column(Integer, ForeignKey('employees.id', ondelete="SET NULL"), nullable=True)

    # Self-referencing relationship: manager and subordinates
    manager = relationship('Employee', remote_side=[id], backref=backref('subordinates', lazy='dynamic'))

    # Relationship to Timesheet
    timesheets = relationship(
        'Timesheet',
        back_populates='employee',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
