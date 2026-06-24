import datetime
from app.database.sqlite_db import engine, Base, SessionLocal
from app.database.models import Appointment

def seed():
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Appointment).count() > 0:
            print("Database already contains appointments. Skipping seeding.")
            return

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)

        appointments = [
            Appointment(
                customer_name="Juan Pérez",
                service_type="Medicina General",
                appointment_date=today.strftime("%Y-%m-%d"),
                appointment_time="10:00",
                contact_info="+51 987 654 321"
            ),
            Appointment(
                customer_name="María López",
                service_type="Odontología",
                appointment_date=tomorrow.strftime("%Y-%m-%d"),
                appointment_time="14:00",
                contact_info="maria.lopez@example.com"
            ),
            Appointment(
                customer_name="Carlos Gómez",
                service_type="Masaje Relajante",
                appointment_date=tomorrow.strftime("%Y-%m-%d"),
                appointment_time="11:00",
                contact_info="+51 955 443 322"
            ),
            Appointment(
                customer_name="Ana Rodríguez",
                service_type="Dermatología",
                appointment_date=day_after.strftime("%Y-%m-%d"),
                appointment_time="16:00",
                contact_info="ana.rod@example.com"
            )
        ]

        db.add_all(appointments)
        db.commit()
        print(f"Successfully seeded {len(appointments)} appointments into the database.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
