from pydantic import BaseModel


class AssignRecommendationInput(BaseModel):
    employee_profile_toon: str
    current_devices_toon: str
    available_devices_toon: str
    max_recommendations: int = 3


class AssignRecommendationOutput(BaseModel):
    toon_result: str

