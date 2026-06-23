from pydantic import BaseModel, Field

class AppointmentBase(BaseModel):
    customer_name: str
    service_type: str
    appointment_date: str = Field(..., description="Format YYYY-MM-DD")
    appointment_time: str = Field(..., description="Format HH:MM")
    contact_info: str

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int

    class Config:
        from_attributes = True
