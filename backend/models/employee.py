from sqlalchemy import Column,Integer,String,ForeignKey,create_engine
from sqlalchemy.orm import relationship,declarative_base,sessionmaker 
from models.base import Base

class Employee(Base):
    __tablename__ ='employees'

    id = Column(Integer,primary_key=True, autoincrement=True)
    employee_name=Column(String(100),nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    manager = relationship('Employee', remote_side=[id], backref='subordinates')

    def as_dict(self):
        """ convert orm object to dictionary """
        return {column.name:getattr(self,column.name) for column in self.__table__.columns}


