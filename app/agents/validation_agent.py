from app.services.gemini_service import gemini_service
import datetime

class ValidationAgent:
    def validate_booking_data(self, state_data: dict, user_message: str) -> dict:
        today = datetime.date.today().strftime("%Y-%m-%d")
        prompt = f"""
        Eres un asistente de IA para una clínica. Tu tarea es validar y extraer datos de reserva de citas.
        Fecha de hoy: {today}
        Datos actuales extraídos de la reserva: {state_data}
        Último mensaje del usuario: "{user_message}"

        Instrucciones:
        1. Extrae del mensaje del usuario los siguientes campos:
           - "customer_name": Nombre del cliente.
           - "service_type": Tipo de servicio (ej. Medicina General, Dermatología, etc.).
           - "appointment_date": Fecha de la cita en formato AAAA-MM-DD. Si el usuario dice "mañana", "pasado mañana", "hoy" o un día de la semana, calcula la fecha exacta basándote en la fecha de hoy ({today}).
           - "appointment_time": Hora de la cita en formato HH:MM (de 24 horas, ej. 11:00, 16:00).
           - "contact_info": Información de contacto (celular, teléfono o correo).
        2. Combina los datos que acabas de extraer con los "Datos actuales extraídos de la reserva". Si un campo ya estaba completo y el usuario no lo cambia, consérvalo.
        3. Verifica si los 5 campos obligatorios están presentes y no son nulos: "customer_name", "service_type", "appointment_date", "appointment_time", "contact_info".
        4. Si falta uno o más campos:
           - "is_complete" debe ser false.
           - En "missing_prompt" escribe una respuesta cordial en español pidiendo amablemente al usuario los datos que faltan (ej. "Por favor, indícame tu nombre y número de contacto para completar la reserva.").
        5. Si todos los 5 campos están completos y validados:
           - "is_complete" debe ser true.
           - "missing_prompt" debe ser null.

        Retorna ÚNICAMENTE un objeto JSON válido con la siguiente estructura (no agregues marcas markdown ni explicaciones):
        {{
            "updated_data": {{
                "customer_name": "nombre o null",
                "service_type": "servicio o null",
                "appointment_date": "AAAA-MM-DD o null",
                "appointment_time": "HH:MM o null",
                "contact_info": "contacto o null"
            }},
            "is_complete": true o false,
            "missing_prompt": "pregunta para pedir datos faltantes o null"
        }}
        """
        return gemini_service.generate_json(prompt)
