from app.database.sqlite_db import SessionLocal
from app.services.appointment_service import AppointmentService
from app.schemas.appointment_schema import AppointmentCreate

class BookingAgent:
    def book_appointment(self, appointment_data: dict) -> dict:
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            appointment = AppointmentCreate(**appointment_data)
            saved_appointment = service.create_appointment(appointment)
            return {"status": "success", "appointment_id": saved_appointment.id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
