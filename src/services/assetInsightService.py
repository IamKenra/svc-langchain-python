import logging
from datetime import datetime, timezone
from typing import Optional

from src.chains.assetInsightChain import getAssetInsightChain
from src.schemas.assetInsightSchema import AssetInsightInput, AssetInsightOutput

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fallback_insight_toon() -> str:
    return """insight:
  current_condition: Insight sementara belum dapat dihasilkan karena model sedang sibuk. Gunakan data maintenance, issue, dan alert sebagai acuan sementara.
  predictive_maintenance: ""

recommendations[1]{text}:
  "Ulangi permintaan insight dalam beberapa menit."
"""


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

    logger.info(
        "Generating asset insight via LLM ts=%s type=%s asset_uuid=%s",
        _utc_now_iso(),
        resolved_type,
        data.asset_uuid,
    )
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
        if toon_result == "":
            logger.warning(
                "assetInsightService empty result ts=%s type=%s asset_uuid=%s -> using fallback TOON",
                _utc_now_iso(),
                resolved_type,
                data.asset_uuid,
            )
            toon_result = _fallback_insight_toon()

        logger.info(
            "assetInsightService: toon_result preview: %s",
            (toon_result[:200] + "...") if len(toon_result) > 200 else toon_result,
        )
        logger.info("LLM asset insight (TOON) generated successfully")

        return AssetInsightOutput(toon_result=toon_result)

    except Exception as e:
        logger.error(
            "Unexpected error in assetInsightService ts=%s type=%s asset_uuid=%s err=%s -> using fallback TOON",
            _utc_now_iso(),
            resolved_type,
            data.asset_uuid,
            str(e),
        )
        return AssetInsightOutput(toon_result=_fallback_insight_toon())
