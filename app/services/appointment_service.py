from sqlalchemy.orm import Session
from app.database import models
from app.schemas.appointment_schema import AppointmentCreate
from typing import List

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_booked_slots(self, date: str) -> List[str]:
        appointments = self.db.query(models.Appointment).filter(
            models.Appointment.appointment_date == date
        ).all()
        return [appt.appointment_time for appt in appointments]

    def create_appointment(self, appointment: AppointmentCreate):
        db_appointment = models.Appointment(
            customer_name=appointment.customer_name,
            service_type=appointment.service_type,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            contact_info=appointment.contact_info
        )
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def get_all_appointments(self):
        return self.db.query(models.Appointment).all()

    def delete_appointment(self, appointment_id: int) -> bool:
        appt = self.db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
        if appt:
            self.db.delete(appt)
            self.db.commit()
            return True
        return False

    def update_appointment(self, appointment_id: int, new_date: str, new_time: str) -> bool:
        appt = self.db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
        if appt:
            appt.appointment_date = new_date
            appt.appointment_time = new_time
            self.db.commit()
            return True
        return False
