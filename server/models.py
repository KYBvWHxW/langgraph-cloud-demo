from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class Assistant(BaseModel):
    id: str = Field(default_factory=lambda: f"asst_{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Thread(BaseModel):
    id: str = Field(default_factory=lambda: f"thread_{uuid.uuid4().hex}")
    assistant_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    messages: List[Dict[str, Any]] = []

class Message(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex}")
    thread_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Deployment(BaseModel):
    id: str = Field(default_factory=lambda: f"deployment_{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"
