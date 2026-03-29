from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()

class register(Base):
    __tablename__ = "users"
    name = Column(String(100))
    email = Column(String(200),primary_key=True,index=True)
    password = Column(String(200))
