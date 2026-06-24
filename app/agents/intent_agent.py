from app.services.gemini_service import gemini_service

class IntentAgent:
    def detect_intent(self, user_message: str) -> dict:
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["horario", "atienden", "abren", "servicio", "precio", "política", "politica", "cancelación", "cancelacion"]):
            return {"intent": "general_query", "entities": {}}
        if any(w in msg_lower for w in ["reservar", "agendar", "cita"]):
            return {"intent": "book_appointment", "entities": {}}
            
        prompt = f"""
        You are an AI assistant for a clinic/salon. Classify the user's intent.
        User Message: "{user_message}"
        Intents: "book_appointment", "check_availability", "general_query", "cancel_appointment", "reschedule_appointment", "unknown".
        Output JSON:
        {{
            "intent": "...",
            "entities": {{
                "date": "YYYY-MM-DD or null",
                "time": "HH:MM or null",
                "service": "string or null",
                "name": "string or null",
                "appointment_id": "integer or null"
            }}
        }}
        """
        return gemini_service.generate_json(prompt)
