import os
from typing import Union

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from src.schemas.serverSchema import *
from src.services.serverService import *
from src.services.devicesService import *
from src.schemas.deviceSchema import *
from src.schemas.assignSchema import AssignRecommendationInput, AssignRecommendationOutput
from src.services.assignService import assignRecommendationService
from src.schemas.assetHealthSchema import (
    AssetHealthHighRiskOutput,
    AssetHealthInput,
    AssetHealthLowRiskOutput,
)
from src.services.assetHealthService import assetHealthService
from src.schemas.assetInsightSchema import AssetInsightInput, AssetInsightOutput
from src.services.assetInsightService import assetInsightService

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

# ====================== AI Router ======================
ai = APIRouter(prefix="/ai", tags=["ai"])


@ai.post("/assign", response_model=AssignRecommendationOutput)
async def RouteAssignRecommendation(
    data: AssignRecommendationInput, token: None = Depends(validate_token)
):
    toon = assignRecommendationService(data)
    return AssignRecommendationOutput(toon_result=toon)


@ai.post("/asset_insight", response_model=AssetInsightOutput)
async def RouteAssetInsight(
    data: AssetInsightInput, token: None = Depends(validate_token)
):
    """
    Endpoint internal untuk menghasilkan AI Insight per asset.
    Dipanggil oleh service Go dengan payload:
    - domain: "ai"
    - context_toon: string TOON
    - asset_uuid: uuid asset (saat ini tidak digunakan langsung oleh chain)
    """
    return assetInsightService(data)

@ai.post(
    "/asset/health",
    response_model=Union[AssetHealthHighRiskOutput, AssetHealthLowRiskOutput],
)
async def RouteAssetHealth(
    data: AssetHealthInput,
    type: str = Query(...),
    token: None = Depends(validate_token),
):
    health_type = type.strip().lower()
    if health_type not in ("high", "low"):
        raise HTTPException(
            status_code=400,
            detail="query parameter 'type' must be 'high' or 'low'",
        )

    return assetHealthService(data, health_type)


router.include_router(ai)
