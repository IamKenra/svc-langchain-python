from fastapi import APIRouter
from src.api.schemas import AssetData, RecommendationResponse
from src.services.recommendation import generate_recommendation

router = APIRouter()

@router.post("/rekomendasi", response_model=RecommendationResponse)
async def get_recommendation(data: AssetData):
    result = generate_recommendation(data)
    return {"recommendation": result}


