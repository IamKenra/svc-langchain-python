from http.client import HTTPException
import os
from fastapi import APIRouter, Depends, Header
from src.api.schemas import *
from src.services.server import *

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

server.get("/status/rightnow", response_model=RecommendationResponse)
async def recommendation(
    data: ServerData,
    token: None = Depends(validate_token)
):
    result = now_summary(data) 
    return result 
