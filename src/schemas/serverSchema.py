from pydantic import BaseModel
from typing import List

class ServerStatusInput(BaseModel):
    cpu: float
    ram: float
    disk: float

class ServerStatusRightNow(BaseModel):
    condition: str
    
class Recommendation(BaseModel):
    title: str
    description: str

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    summary: str