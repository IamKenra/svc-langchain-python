from http.client import HTTPException
import os
from fastapi import APIRouter, Depends, Header
from src.api.schemas import *
from services.server import generate_recommendation

router = APIRouter()

def validate_token(x_token: str = Header(...)) -> None:
    if x_token != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

# health check
@router.get("/health")
async def health_check():
    return {"status": "ok"}

# server
server = APIRouter(prefix="/server", tags=["server"])

server.post("/status", response_model=RecommendationResponse)
async def get_recommendation(
    data: ServerData,
    token: None = Depends(validate_token)
):
    result = generate_recommendation(data) 
    return result 
