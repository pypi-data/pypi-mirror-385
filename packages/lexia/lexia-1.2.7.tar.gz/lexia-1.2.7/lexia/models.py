"""
Lexia Models
============

Pydantic models for Lexia API communication.
"""

from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel


class Memory(BaseModel):
    """Memory model for structured user memory data from Lexia request."""
    name: str = ""
    goals: List[str] = []
    location: str = ""
    interests: List[str] = []
    preferences: List[str] = []
    past_experiences: List[str] = []


class Variable(BaseModel):
    """Variable model for environment variables from Lexia request."""
    name: str
    value: str


class ChatMessage(BaseModel):
    """Request model for chat messages matching Lexia's expected format."""
    thread_id: str
    model: str
    message: str
    conversation_id: int
    response_uuid: str
    message_uuid: str
    channel: str
    file_type: str = ""
    file_url: str = ""
    variables: List[Variable]
    url: str
    url_update: str = ""
    url_upload: str = ""
    force_search: bool = False
    force_code: Optional[bool] = None
    system_message: Optional[str] = None
    memory: Union[Memory, Dict[str, Any], List] = Memory()
    project_system_message: Optional[str] = None
    first_message: bool = False
    project_id: str = ""
    project_files: Optional[Any] = None
    stream_url: Optional[str] = None
    stream_token: Optional[str] = None
    headers: Optional[Dict[str, str]] = None


class ChatResponse(BaseModel):
    """Response model for chat requests matching Lexia's expected format."""
    status: str
    message: str
    response_uuid: str
    thread_id: str
