import logging
from typing import Optional

from src.chains.assetInsightChain import getAssetInsightChain
from src.schemas.assetInsightSchema import AssetInsightInput, AssetInsightOutput

logger = logging.getLogger(__name__)


def infer_insight_type_from_context(context_toon: str) -> str:
    lowered = (context_toon or "").lower()

    # Backend baru mengirimkan blok insight_context/insight_constraints
    # agar service bisa memilih prompt non-monitoring secara eksplisit.
    if "monitoring_capability: non_monitoring" in lowered:
        return "non_monitoring"
    if "insight_mode: non_monitoring" in lowered:
        return "non_monitoring"

    return "monitoring"


def assetInsightService(data: AssetInsightInput, insight_type: Optional[str] = None) -> AssetInsightOutput:
    resolved_type = (insight_type or "").strip().lower()
    if resolved_type == "":
        resolved_type = infer_insight_type_from_context(data.context_toon)

    if resolved_type not in ("monitoring", "non_monitoring"):
        raise ValueError("insight_type must be 'monitoring' or 'non_monitoring'")

    logger.info("Generating asset insight via LLM type=%s", resolved_type)
    logger.info(
        "assetInsightService: context_toon preview: %s",
        (data.context_toon[:200] + "...") if len(data.context_toon) > 200 else data.context_toon,
    )

    try:
        chain = getAssetInsightChain(resolved_type)
        result = chain.invoke(
            {
                "context_toon": data.context_toon,
            }
        )

        if not isinstance(result, str):
            logger.warning("LLM result is not a string, casting to str")
            result = str(result)

        toon_result = result.strip()

        logger.info(
            "assetInsightService: toon_result preview: %s",
            (toon_result[:200] + "...") if len(toon_result) > 200 else toon_result,
        )
        logger.info("LLM asset insight (TOON) generated successfully")

        return AssetInsightOutput(toon_result=toon_result)

    except Exception as e:
        logger.error(f"Unexpected error in assetInsightService: {e}")
        raise
