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
        if self.state["current_flow"] == "booking":
            return self._handle_booking_flow(user_message)

        intent_response = self.intent_agent.detect_intent(user_message)
        intent = intent_response.get("intent", "unknown")
        entities = intent_response.get("entities", {})

        print(f"--- LOG ORCHESTRATOR ---")
        print(f"Mensaje recibido: {user_message}")
        print(f"Resultado IntentAgent: {intent_response}")
        print(f"Intent detectado: {intent}")
        print(f"------------------------")

        if intent == "general_query":
            return self.rag_agent.answer_query(user_message)
        elif intent == "check_availability":
            date = entities.get("date")
            if not date: return "¿Para qué fecha quieres consultar?"
            avail = self.availability_agent.check_availability(date)
            return f"Para {date}, horarios disponibles: {', '.join(avail.get('available_slots', []))}"
        elif intent == "book_appointment":
            self.state["current_flow"] = "booking"
            self.state["appointment_data"] = entities
            return self._handle_booking_flow(user_message)
        elif intent in ["cancel_appointment", "reschedule_appointment"]:
            return "Actualmente solo soportamos crear citas y responder preguntas. La cancelación o reprogramación está en desarrollo."
        
        return "Lo siento, no entendí tu solicitud."

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
