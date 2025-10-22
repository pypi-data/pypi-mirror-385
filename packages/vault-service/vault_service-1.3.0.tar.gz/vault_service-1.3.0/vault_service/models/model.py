from pydantic import BaseModel
from typing import Dict, Any

class SecretData(BaseModel):
    data: Dict[str, Any]  # Accepts any JSON structure as a dictionary
