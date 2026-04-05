from typing import List, Literal
from pydantic import BaseModel


AssetHealthType = Literal["high", "low"]


class AssetHealthInput(BaseModel):
    asset_uuid: str
    context_toon: str


class AssetHealthHighRiskOutput(BaseModel):
    lifecycle_score: float
    confidence: float
    top_factors: List[str]


class AssetHealthLowRiskOutput(BaseModel):
    final_health_status: Literal["HEALTHY", "WARNING", "CRITICAL"]
    final_health_score: float
    confidence: float
    top_factors: List[str]
