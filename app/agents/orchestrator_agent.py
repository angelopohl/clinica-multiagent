import datetime
from app.database.sqlite_db import SessionLocal
from app.services.appointment_service import AppointmentService
from app.agents.intent_agent import IntentAgent
from app.agents.rag_agent import RagAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.availability_agent import AvailabilityAgent
from app.agents.booking_agent import BookingAgent
from app.agents.notification_agent import NotificationAgent

class OrchestratorAgent:
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.rag_agent = RagAgent()
        self.validation_agent = ValidationAgent()
        self.availability_agent = AvailabilityAgent()
        self.booking_agent = BookingAgent()
        self.notification_agent = NotificationAgent()
        self.state = {"current_flow": None, "appointment_data": {}}

    def process_message(self, user_message: str) -> str:
        intent_response = self.intent_agent.detect_intent(user_message)
        intent = intent_response.get("intent", "unknown")
        entities = intent_response.get("entities", {})

        print(f"--- LOG ORCHESTRATOR ---")
        print(f"Mensaje recibido: {user_message}")
        print(f"Resultado IntentAgent: {intent_response}")
        print(f"Intent detectado: {intent}")
        print(f"------------------------")

        # Si se detecta un intento explícito diferente a "unknown", interrumpimos cualquier flujo anterior
        if intent in ["general_query", "cancel_appointment", "reschedule_appointment", "check_availability"]:
            self.state = {"current_flow": None, "appointment_data": {}}
            
            if intent == "general_query":
                return self.rag_agent.answer_query(user_message)
            elif intent == "check_availability":
                date = entities.get("date")
                if not date: return "¿Para qué fecha quieres consultar?"
                avail = self.availability_agent.check_availability(date)
                return f"Para {date}, horarios disponibles: {', '.join(avail.get('available_slots', []))}"
            elif intent == "cancel_appointment":
                self.state["current_flow"] = "cancellation"
                self.state["cancellation_data"] = entities or {}
                return self._handle_cancellation_flow(user_message)
            elif intent == "reschedule_appointment":
                self.state["current_flow"] = "rescheduling"
                self.state["reschedule_data"] = entities or {}
                return self._handle_rescheduling_flow(user_message)

        # Si no hay nuevo intento explícito, continuamos con el flujo activo
        if self.state.get("current_flow") == "booking":
            return self._handle_booking_flow(user_message)
        elif self.state.get("current_flow") == "cancellation":
            return self._handle_cancellation_flow(user_message)
        elif self.state.get("current_flow") == "rescheduling":
            return self._handle_rescheduling_flow(user_message)

        # Si no hay flujo activo pero detectamos un intento de reserva
        if intent == "book_appointment":
            self.state["current_flow"] = "booking"
            self.state["appointment_data"] = entities
            return self._handle_booking_flow(user_message)
        
        return "Lo siento, no entendí tu solicitud. ¿Te gustaría agendar, cancelar o reprogramar una cita?"

    def _handle_booking_flow(self, user_message: str) -> str:
        validation = self.validation_agent.validate_booking_data(self.state["appointment_data"], user_message)
        if "updated_data" in validation:
            self.state["appointment_data"] = validation["updated_data"]
            
        if not validation.get("is_complete"):
            return validation.get("missing_prompt", "Faltan datos.")
            
        date = self.state["appointment_data"].get("appointment_date")
        time = self.state["appointment_data"].get("appointment_time")
        
        avail = self.availability_agent.check_availability(date, time)
        if avail["status"] == "unavailable":
            self.state["appointment_data"]["appointment_time"] = None
            return f"Horario no disponible. Alternativas: {', '.join(avail.get('alternatives', []))}."
            
        booking_res = self.booking_agent.book_appointment(self.state["appointment_data"])
        if booking_res["status"] == "success":
            msg = self.notification_agent.send_confirmation(self.state["appointment_data"], booking_res["appointment_id"])
            self.state = {"current_flow": None, "appointment_data": {}}
            return msg
        return "Hubo un error al reservar."

    def _handle_cancellation_flow(self, user_message: str) -> str:
        data = self.state.get("cancellation_data", {})
        
        import re
        appt_id = data.get("appointment_id")
        if not appt_id:
            match = re.search(r'\b\d+\b', user_message)
            if match:
                appt_id = int(match.group(0))
                data["appointment_id"] = appt_id
                
        if not appt_id:
            return "Por favor, indícame el ID de la cita que deseas cancelar (ejemplo: 3)."
            
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            success = service.delete_appointment(appt_id)
            self.state = {"current_flow": None, "appointment_data": {}}
            if success:
                return f"Tu cita con ID {appt_id} ha sido cancelada exitosamente."
            else:
                return f"No encontré ninguna cita registrada con el ID {appt_id}."
        finally:
            db.close()

    def _handle_rescheduling_flow(self, user_message: str) -> str:
        data = self.state.get("reschedule_data", {})
        if not data:
            data = {}
            self.state["reschedule_data"] = data
            
        import re
        
        if not data.get("appointment_id"):
            match = re.search(r'\b\d+\b', user_message)
            if match:
                data["appointment_id"] = int(match.group(0))
                
        if not data.get("date"):
            match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', user_message)
            if match:
                data["date"] = match.group(0)
                
        if not data.get("time"):
            match = re.search(r'\b\d{2}:\d{2}\b', user_message)
            if match:
                data["time"] = match.group(0)

        missing_fields = []
        if not data.get("appointment_id"): missing_fields.append("el ID de tu cita")
        if not data.get("date"): missing_fields.append("la nueva fecha (AAAA-MM-DD)")
        if not data.get("time"): missing_fields.append("la nueva hora (HH:MM)")
        
        if missing_fields:
            prompt = f"""
            Extract entities for rescheduling.
            Current data: {data}
            Latest message: "{user_message}"
            Extract "appointment_id" (int), "date" (YYYY-MM-DD), and "time" (HH:MM) from the message and return them.
            If date is relative like "mañana" or "pasado mañana", assume today is {datetime.date.today().strftime('%Y-%m-%d')}.
            Output JSON format:
            {{
                "appointment_id": int or null,
                "date": "YYYY-MM-DD" or null,
                "time": "HH:MM" or null
            }}
            """
            try:
                extracted = self.intent_agent.gemini_service.generate_json(prompt)
                for k, v in extracted.items():
                    if v and not data.get(k):
                        data[k] = v
            except Exception:
                pass
                
        missing_fields = []
        if not data.get("appointment_id"): missing_fields.append("el ID de tu cita")
        if not data.get("date"): missing_fields.append("la nueva fecha (AAAA-MM-DD)")
        if not data.get("time"): missing_fields.append("la nueva hora (HH:MM)")
        
        if missing_fields:
            return f"Para reprogramar, por favor indícame: {', '.join(missing_fields)}."
            
        appt_id = int(data["appointment_id"])
        date = data["date"]
        time = data["time"]
        
        avail = self.availability_agent.check_availability(date, time)
        if avail["status"] == "unavailable":
            data["time"] = None
            return f"Ese horario ({time}) no está disponible para la fecha {date}. Alternativas: {', '.join(avail.get('alternatives', []))}. Por favor indica una de ellas."
            
        db = SessionLocal()
        try:
            service = AppointmentService(db)
            success = service.update_appointment(appt_id, date, time)
            self.state = {"current_flow": None, "appointment_data": {}}
            if success:
                return f"Tu cita con ID {appt_id} ha sido reprogramada exitosamente para el {date} a las {time}."
            else:
                return f"No encontré ninguna cita registrada con el ID {appt_id}."
        finally:
            db.close()
