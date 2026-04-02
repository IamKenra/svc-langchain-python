from langchain.prompts import PromptTemplate
from src.clients.llm_client import llm_client

assetInsightTemplate = PromptTemplate(
    template="""
You are an expert SRE / infrastructure engineer.
You receive monitoring context in TOON format for one IT asset.

Context (TOON):
{context_toon}

Your task:
- Explain the current technical condition of the asset (CPU/RAM/Disk/Network) in clear, concise language.
- Provide short predictive maintenance insight (if possible) based on trends and alerts.
- Provide concrete, actionable recommendations (operations / capacity / monitoring).

Notes:
- Treat percentages as utilization (e.g. cpu_avg_pct = 80 means 80% CPU usage).
- Network values are in kilobits per second (kbps).
- Health.status in TOON is the rule-based health status calculated by the core system; use it as a guide, do not override it.

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

assetInsightChain = assetInsightTemplate | llm_client
