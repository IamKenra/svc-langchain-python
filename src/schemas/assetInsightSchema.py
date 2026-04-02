from pydantic import BaseModel
from typing import List, Optional


class AssetInsightInput(BaseModel):
    # domain dikirim oleh service Go (contoh: "ai"), tetapi saat ini
    # belum digunakan secara eksplisit di chain.
    domain: str
    context_toon: str
    asset_uuid: str


class AssetInsightOutput(BaseModel):
    toon_result: str
