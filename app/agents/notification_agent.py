class NotificationAgent:
    def send_confirmation(self, appointment_data: dict, appointment_id: int) -> str:
        return f"Tu cita para {appointment_data.get('service_type')} el {appointment_data.get('appointment_date')} a las {appointment_data.get('appointment_time')} ha sido confirmada con éxito. ID: {appointment_id}."
