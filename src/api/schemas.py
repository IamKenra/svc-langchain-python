from pydantic import BaseModel
from typing import Optional

class ServerData(BaseModel):
    cpu_usage: float
    ram_usage: float  
    disk_usage: float 
    server_id: Optional[str] = None  

class RecommendationResponse(BaseModel):
    recommendation: str  