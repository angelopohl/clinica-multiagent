from sqlalchemy import Column, Integer, String
from app.database.sqlite_db import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    service_type = Column(String)
    appointment_date = Column(String)
    appointment_time = Column(String)
    contact_info = Column(String)
