from http.client import HTTPException
import os
from fastapi import APIRouter, Depends, Header
from src.schemas.serverSchema import *
from src.services.serverService import *
from src.services.devicesService import *
from src.schemas.deviceSchema import *

router = APIRouter()

def validate_token(x_token: str = Header(...)) -> None:
    if x_token != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

# health check
@router.get("/health")
async def health_check():
    return {"status": "ok"}

# ====================== Server Routes ======================
server = APIRouter(prefix="/server", tags=["server"])

@server.post("/status/rightnow", response_model=ServerStatusRightNow)
async def RouteRightNow(
    data: ServerStatusInput,
    token: None = Depends(validate_token)
):
    result = RightNowCondition(data) 
    return result 

router.include_router(server)

# ====================== Device Router ======================
device = APIRouter(prefix="/device", tags=["device"]) 
@device.post("/recommendation", response_model=deviceRecomendationRespone)
async def RouteDeviceRecommendation(
    data: deviceRecomendationInput,
    token: None = Depends(validate_token)
):
    result = deviceRecomendationService(data)
    return result

router.include_router(device)