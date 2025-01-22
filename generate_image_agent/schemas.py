from pydantic import BaseModel
from typing import Dict, Optional, Union

class InputSchema(BaseModel):
    tool_name: str
    prompt: str
    input_dir: Optional[str] = None

class SystemPromptSchema(BaseModel):
    """Schema for system prompts."""
    role: str = "You are a helpful AI assistant."
    persona: Optional[Union[Dict, BaseModel]] = None