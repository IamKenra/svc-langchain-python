from langchain.prompts import PromptTemplate
from src.clients.llm_client import llm_client

assetInsightMonitoringTemplate = PromptTemplate(
    template="""
You are an expert SRE / infrastructure engineer.
You receive monitoring context in TOON format for one IT asset.

Context (TOON):
{context_toon}

Your task:
- Explain the current technical condition of the asset using available telemetry, alerts, and history.
- Provide short predictive maintenance insight (if possible) based on trends and alerts.
- Provide concrete, actionable recommendations (operations / capacity / monitoring).

Notes:
- Treat percentages as utilization (e.g. cpu_avg_pct = 80 means 80% CPU usage).
- Network values are in kilobits per second (kbps).
- Health snapshot is a guide from core system; do not override it.

OUTPUT FORMAT (VERY IMPORTANT):
Reply ONLY with TOON, no extra text, no explanation:

insight:
  current_condition: one short paragraph, max 3 sentences
  predictive_maintenance: one short paragraph OR "" (empty) if not enough data

recommendations[n]{{text}}:
  "short recommendation 1"
  "short recommendation 2"

Rules:
- Do NOT add any prose or explanation outside the TOON blocks.
- Do NOT wrap the output with markdown fences.
- Use exactly the keys: current_condition, predictive_maintenance.
""",
    input_variables=["context_toon"],
)

assetInsightNonMonitoringTemplate = PromptTemplate(
    template="""
You are an IT asset reliability analyst.
You receive non-monitoring context in TOON format for one IT asset.

Context (TOON):
{context_toon}

Your task:
- Explain the current condition using maintenance history, known issues, alerts, and health snapshot.
- Provide short predictive maintenance insight based on lifecycle signal (ageing, repeated issue, maintenance pattern).
- Provide concrete, actionable recommendations.

Critical constraints:
- This is NON-MONITORING mode.
- Do NOT mention CPU, RAM, Disk, Network, throughput, or telemetry percentages.
- If monitoring metrics are not available, never infer compute telemetry values.

OUTPUT FORMAT (VERY IMPORTANT):
Reply ONLY with TOON, no extra text, no explanation:

insight:
  current_condition: one short paragraph, max 3 sentences
  predictive_maintenance: one short paragraph OR "" (empty) if not enough data

recommendations[n]{{text}}:
  "short recommendation 1"
  "short recommendation 2"

Rules:
- Do NOT add any prose or explanation outside the TOON blocks.
- Do NOT wrap the output with markdown fences.
- Use exactly the keys: current_condition, predictive_maintenance.
""",
    input_variables=["context_toon"],
)

assetInsightMonitoringChain = assetInsightMonitoringTemplate | llm_client
assetInsightNonMonitoringChain = assetInsightNonMonitoringTemplate | llm_client


def getAssetInsightChain(insight_type: str):
    normalized = (insight_type or "").strip().lower()
    if normalized == "non_monitoring":
        return assetInsightNonMonitoringChain
    return assetInsightMonitoringChain
