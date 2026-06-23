from app.services.gemini_service import gemini_service
import datetime

class ValidationAgent:
    def validate_booking_data(self, state_data: dict, user_message: str) -> dict:
        prompt = f"""
        Verify appointment details.
        Current data: {state_data}
        Latest message: "{user_message}"
        Task: Extract entities, merge with current data, check if all required fields are present: "customer_name", "service_type", "appointment_date", "appointment_time", "contact_info".
        If incomplete, generate "missing_prompt".
        Output JSON:
        {{
            "updated_data": {{ "customer_name": "...", "service_type": "...", "appointment_date": "...", "appointment_time": "...", "contact_info": "..." }},
            "is_complete": true/false,
            "missing_prompt": "string or null"
        }}
        """
        return gemini_service.generate_json(prompt)
