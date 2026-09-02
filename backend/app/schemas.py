from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

Severity = Literal["Normal", "Warning", "Critical"]
StationStatus = Literal["Normal", "Warning", "Critical"]

class SensorReading(BaseModel):
    station_id: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=-80, le=80)
    pressure: float = Field(..., ge=850, le=1100)
    humidity: float = Field(..., ge=0, le=100)
    timestamp: Optional[datetime] = None

class AnomalyResponse(BaseModel):
    station_id: str
    timestamp: datetime
    temperature: float
    pressure: float
    humidity: float
    anomaly: bool
    anomaly_score: float
    confidence: float
    severity: Severity
    root_cause: str
    corrected_values: Optional[dict] = None
    explanation: str
    feature_contributions: dict
    sensor_health: float

class AlertUpdate(BaseModel):
    status: Literal["Active", "Resolved"]

class StationCreate(BaseModel):
    station_id: str
    name: str
    latitude: float
    longitude: float

class SimulationRequest(BaseModel):
    station_id: str = "Chennai AWS-01"
    anomaly_type: Literal["temperature_spike","pressure_shift","humidity_spike","frozen_value","communication_error"] = "temperature_spike"
