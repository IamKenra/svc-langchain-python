from langchain.prompts import PromptTemplate
from src.clients.llm_client import llm_client

assetHealthHighRiskTemplate = PromptTemplate(
    template="""
You are an IT asset health scoring engine.
You will receive one asset context in TOON format.

Context (TOON):
{context_toon}

Task for HIGH risk mode:
- Analyze lifecycle degradation risk from the given evidence.
- Compute lifecycle_score in range 0..100 (higher is healthier).
- Compute confidence in range 0..100 based on evidence quality and consistency.
- Return max 3 top_factors directly supported by context_toon.

Scoring baseline (must be applied):
- Evaluate 4 dimensions: AlertRisk, TrendRisk, ReliabilityEventRisk, AssetContextRisk.
- Use weighted aggregation:
  GlobalRisk = 0.40*AlertRisk + 0.30*TrendRisk + 0.20*ReliabilityEventRisk + 0.10*AssetContextRisk.
- lifecycle_score = clamp(100 - GlobalRisk, 0, 100).

Output rules:
- Reply ONLY valid JSON (no markdown fence, no extra prose).
- JSON keys must be exactly:
  - lifecycle_score (number)
  - confidence (number)
  - top_factors (array of 1..3 strings)
""",
    input_variables=["context_toon"],
)

assetHealthLowRiskTemplate = PromptTemplate(
    template="""
You are an IT asset health scoring engine.
You will receive one asset context in TOON format.

Context (TOON):
{context_toon}

Task for LOW risk mode:
- Produce final health status and final score.
- Compute final_health_score in range 0..100 (higher is healthier).
- Compute confidence in range 0..100 based on evidence quality and consistency.
- Return max 3 top_factors directly supported by context_toon.

Scoring baseline (must be applied):
- Evaluate 4 dimensions: AlertRisk, TrendRisk, ReliabilityEventRisk, AssetContextRisk.
- Use weighted aggregation:
  GlobalRisk = 0.40*AlertRisk + 0.30*TrendRisk + 0.20*ReliabilityEventRisk + 0.10*AssetContextRisk.
- final_health_score = clamp(100 - GlobalRisk, 0, 100).

Status mapping (must be consistent with score):
- score >= 80 => HEALTHY
- 60 <= score < 80 => WARNING
- score < 60 => CRITICAL

Output rules:
- Reply ONLY valid JSON (no markdown fence, no extra prose).
- JSON keys must be exactly:
  - final_health_status (HEALTHY|WARNING|CRITICAL)
  - final_health_score (number)
  - confidence (number)
  - top_factors (array of 1..3 strings)
""",
    input_variables=["context_toon"],
)

assetHealthHighRiskChain = assetHealthHighRiskTemplate | llm_client
assetHealthLowRiskChain = assetHealthLowRiskTemplate | llm_client
