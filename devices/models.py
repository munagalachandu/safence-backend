from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import Dict


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Device(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str
    name: str
    type: str
    status: str
    voltage: float
    last_heartbeat: datetime
    location: Dict[str, float]
    alerts_count: int = 0

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
