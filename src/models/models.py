from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ultron.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class RegisteredDevice(Base):
    __tablename__ = "devices"
    device_id = Column(String, primary_key=True)
    label = Column(String, nullable=True)
    flavor = Column(String, nullable=False)  # 'tasker' | 'macrodroid'
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    auth_token = Column(String, nullable=True)
    active = Column(Boolean, default=True)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id = Column(Integer, primary_key=True, auto_increment=True)
    correlate_id = Column(String, index=True, nullable=True)
    device_id = Column(String, index=True)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response = Column(String, nullable=True)

Base.metadata.create_all(engine)
