from pydantic import BaseModel
from typing import List

class device(BaseModel) :
    device_id: str
    device_type: str
    device_model: str
    spesification: str
    status: str

class deviceRecomendationInput(BaseModel):
    role_position: str
    device_list: List[device]

class deviceRecomendationRespone(BaseModel):
    device_id: str
    device_model: str
    summary: str