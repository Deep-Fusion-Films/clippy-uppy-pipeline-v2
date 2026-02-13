from pydantic import BaseModel
from typing import Optional, Dict, Any

class GcsEvent(BaseModel):
    bucket: str
    name: str
    metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None

class UnifiedAsset(BaseModel):
    asset_id: str
    source: str
    bucket: str
    file_name: str
    metadata: Dict[str, Any]
    correlation_id: str
    trace_id: str

