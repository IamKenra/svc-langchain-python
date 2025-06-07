from http.client import HTTPException
import os
from fastapi import APIRouter, Depends, Header
from src.schemas.serverSchema import *
from src.services.serverService import *

router = APIRouter()

def validate_token(x_token: str = Header(...)) -> None:
    if x_token != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

# health check
@router.get("/health")
async def health_check():
    return {"status": "ok"}

server = APIRouter(prefix="/server", tags=["server"])

@server.post("/status/rightnow", response_model=RecommendationResponse)
async def recommendation(
    data: ServerStatusInput,
    token: None = Depends(validate_token)
):
    result = generate_server_recommendation(data) 
    return result 

router.include_router(server)