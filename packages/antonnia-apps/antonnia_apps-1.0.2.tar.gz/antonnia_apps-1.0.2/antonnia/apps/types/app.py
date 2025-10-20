from datetime import datetime
from typing import Dict, Optional, TypedDict
from pydantic import BaseModel

class App(BaseModel):
    id: str
    organization_id: Optional[str] = None
    name: str
    webhook: str
    webhook_headers: Optional[Dict[str, str]] = None
    created_at: datetime
    # updated_at: datetime TODO: create updated_at field

class AppUpdateFields(TypedDict):
    name: Optional[str]
    webhook: Optional[str]
    webhook_headers: Optional[Dict[str, str]]
