from fastapi import APIRouter
from pydantic import BaseModel
from src.api.schemas import AssetData
from src.services.recommendation import generate_recommendation

router = APIRouter()

class RecommendationResponse(BaseModel):
    recommendations: list[dict]
    summary: str

@router.post("/rekomendasi", response_model=RecommendationResponse)
async def get_recommendation(data: AssetData):
    result = generate_recommendation(data)  # Hasil sudah dalam format dict
    return result  # FastAPI akan otomatis mengonversi ke JSON
