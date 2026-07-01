from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database.sqlite_db import engine, Base
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from app.agents.orchestrator_agent import OrchestratorAgent
from app.services.appointment_service import AppointmentService
from app.database.sqlite_db import SessionLocal

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Appointment Multi-Agent System",
    description="A multi-agent system for booking appointments using Gemini and RAG",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    # Auto-ingest RAG documents on startup if ChromaDB is empty
    try:
        from app.vectorstore.chroma_store import chroma_store
        if chroma_store.collection.count() == 0:
            print("ChromaDB is empty. Auto-ingesting documents...")
            from app.vectorstore.ingest_documents import ingest
            ingest()
    except Exception as e:
        print(f"Error on startup RAG ingestion: {e}")


# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Sistema multiagente de reservas activo"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to process user messages via the multi-agent system.
    """
    response_message = orchestrator.process_message(request.message)
    return ChatResponse(response=response_message)

@app.post("/appointments", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate):
    """
    Direct endpoint to create an appointment.
    """
    db = SessionLocal()
    try:
        service = AppointmentService(db)
        return service.create_appointment(appointment)
    finally:
        db.close()

@app.get("/appointments", response_model=list[AppointmentResponse])
def list_appointments():
    """
    List all appointments.
    """
    db = SessionLocal()
    try:
        service = AppointmentService(db)
        return service.get_all_appointments()
    finally:
        db.close()

@app.get("/availability")
def get_availability(date: str):
    """
    Get available slots for a given date (YYYY-MM-DD).
    """
    db = SessionLocal()
    try:
        service = AppointmentService(db)
        # Default working hours 9 AM to 5 PM
        all_slots = [f"{hour:02d}:00" for hour in range(9, 18)]
        booked_slots = service.get_booked_slots(date)
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        return {"date": date, "available_slots": available_slots}
    finally:
        db.close()

# Mount frontend static files as a fallback (after API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

