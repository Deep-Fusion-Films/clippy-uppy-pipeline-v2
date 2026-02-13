from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Person(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None


class ObjectItem(BaseModel):
    label: str
    confidence: Optional[float] = None


class Environment(BaseModel):
    location_type: Optional[str] = None
    setting: Optional[str] = None
    time_of_day: Optional[str] = None


class Camera(BaseModel):
    movement: Optional[str] = None
    framing: Optional[str] = None
    style: Optional[str] = None


class ClipMetadata(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    people: List[Person] = []
    objects: List[ObjectItem] = []
    environment: Optional[Environment] = None
    camera: Optional[Camera] = None
    tags: List[str] = []
    raw_model_output: Optional[Dict[str, Any]] = None

