from app.database.sqlite_db import SessionLocal
from app.services.appointment_service import AppointmentService

class AvailabilityAgent:
    def check_availability(self, date: str, requested_time: str = None) -> dict:
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            all_slots = [f"{hour:02d}:00" for hour in range(9, 18)]
            booked_slots = service.get_booked_slots(date)
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            
            if requested_time:
                if requested_time in available_slots:
                    return {"status": "available", "time": requested_time, "alternatives": []}
                else:
                    return {"status": "unavailable", "time": requested_time, "alternatives": available_slots[:3]}
            return {"status": "info", "available_slots": available_slots}
        finally:
            db.close()
