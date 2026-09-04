from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

Severity = Literal['Normal', 'Warning', 'Critical']
StationStatus = Literal['Normal', 'Warning', 'Critical']

class SensorReading(BaseModel):
    station_id: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=-80, le=80)
    pressure: float = Field(..., ge=850, le=1100)
    humidity: float = Field(..., ge=0, le=100)
    timestamp: Optional[datetime] = None

class AlertUpdate(BaseModel):
    status: Literal['Active', 'Resolved']

class StationCreate(BaseModel):
    station_id: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class SimulationRequest(BaseModel):
    station_id: str
    anomaly_type: Literal['temperature_spike','pressure_shift','humidity_spike','multi_parameter_spike','frozen_value','communication_error','normal'] = 'temperature_spike'
    count: int = Field(default=1, ge=1, le=20)

class AdminLogin(BaseModel):
    username: str
    password: str

class MonitorConfig(BaseModel):
    enabled: bool
    interval_seconds: int = Field(default=5, ge=2, le=60)
