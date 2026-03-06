from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from datetime import time


class StopType(str, Enum):
    PICKUP = "pickup"
    DROPOFF = "dropoff"


class StopCreate(BaseModel):
    run_id: int
    type: str
    sequence: Optional[int] = None
    name: Optional[str] = None
    address: Optional[str] = None
    planned_time: Optional[time] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StopUpdate(BaseModel):
    sequence: int | None = None
    type: StopType | None = None
    run_id: int | None = None
    name: str | None = None
    address: str | None = None
    planned_time: time | None = None
    latitude: float | None = None
    longitude: float | None = None


class StopOut(BaseModel):
    id: int
    sequence: int
    type: StopType
    run_id: int
    name: str | None = None
    address: str | None = None
    planned_time: time | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = ConfigDict(from_attributes=True)


class StopReorder(BaseModel):
    new_sequence: int
