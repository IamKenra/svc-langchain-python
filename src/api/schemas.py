from pydantic import BaseModel
from typing import Optional

class AssetData(BaseModel):
    cpu_usage: float  # Persentase penggunaan CPU
    ram_usage: float  # Persentase penggunaan RAM
    disk_usage: float  # Persentase penggunaan disk
    server_id: Optional[str] = None  # ID server (opsional)

class RecommendationResponse(BaseModel):
    recommendation: str  # Hasil rekomendasi dari LLM