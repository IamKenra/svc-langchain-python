from langchain.prompts import PromptTemplate
from src.clients.llm_client import llm_client

assignRecommendationTemplate = PromptTemplate(
  template="""
  You are an expert in managing IT inventory at a large company.
  Your task is to provide recommendations for devices to be assigned to an employee.

  Employee profile data (TOON):
  {employee_profile_toon}

  Devices currently used by the employee (TOON, can be empty):
  {current_devices_toon}

  List of devices available for assignment (TOON):
  {available_devices_toon}

  Recommendation objectives:
  - Devices must match the employee's position/role and seniority level.
  - If the employee already has a functional laptop, prioritize recommending supporting devices
    such as monitor, keyboard, mouse, or dongle before replacing the laptop.
  - Maximize the use of existing devices (reuse). The devices don't need to be the newest,
    as long as the specifications are sufficient and the lifespan is reasonable for the role.
  - Do not recommend the same device more than once.

  Important rules:
  - Only select asset_uuid from the available_devices table; do not create new UUIDs.
  - If no perfectly suitable device exists, still provide the best recommendation available,
    and explain the limitations in the reason column.
  - Maximum number of recommendations is {max_recommendations}.

  OUTPUT FORMAT:
  Reply ONLY with TOON in the following format, with no text outside the TOON:

  recommendations[n]{{asset_uuid,asset_type,asset_model,priority,reason}}:
    uuid-1,laptop,Dell Latitude 7490,1,"brief reason"
    uuid-2,monitor,Dell 24,2,"brief reason"

  Where:
  - n = number of recommendations (maximum {max_recommendations}).
  - asset_uuid is taken from the asset_uuid column in available_devices.
  - asset_type is a short category, for example: "laptop", "monitor", "mouse", "keyboard", "dongle".
  - asset_model is the model/brand name that is easy to understand by the user.
  - priority is the number 1 for the best recommendation, then 2, 3, etc.
  - reason is a brief explanation in English.

  Ensure:
  - TOON is valid and consistent.
  - No explanatory text outside the TOON block.
  """,
  input_variables=[
    "employee_profile_toon",
    "current_devices_toon",
    "available_devices_toon",
    "max_recommendations",
  ],
)

assignRecommendation = assignRecommendationTemplate | llm_client

