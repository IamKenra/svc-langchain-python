import json
import logging
import re
from typing import Any, Dict, List, Union, cast

from src.chains.assetHealthChain import (
    assetHealthHighRiskChain,
    assetHealthLowRiskChain,
)
from src.schemas.assetHealthSchema import (
    AssetHealthHighRiskOutput,
    AssetHealthInput,
    AssetHealthLowRiskOutput,
    AssetHealthType,
)

logger = logging.getLogger(__name__)

ALLOWED_FINAL_STATUS = {"HEALTHY", "WARNING", "CRITICAL"}


def _clamp_0_100(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field_name}") from exc

    return max(0.0, min(100.0, number))


def _normalize_top_factors(raw: Any) -> List[str]:
    if isinstance(raw, list):
        factors = [str(item).strip() for item in raw if str(item).strip()]
    elif isinstance(raw, str):
        value = raw.strip()
        factors = [value] if value else []
    else:
        factors = []

    if not factors:
        raise ValueError("top_factors must contain at least 1 item")

    return factors[:3]


def _extract_json_payload(raw_result: str) -> Dict[str, Any]:
    text = raw_result.strip()
    if not text:
        raise ValueError("empty llm response")

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return cast(Dict[str, Any], payload)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("invalid llm response format")

    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid llm response format") from exc

    if not isinstance(payload, dict):
        raise ValueError("invalid llm response format")

    return cast(Dict[str, Any], payload)


def _status_from_score(score: float) -> str:
    if score >= 80:
        return "HEALTHY"
    if score >= 60:
        return "WARNING"
    return "CRITICAL"


def _build_high_response(payload: Dict[str, Any]) -> AssetHealthHighRiskOutput:
    lifecycle_score = _clamp_0_100(payload.get("lifecycle_score"), "lifecycle_score")
    confidence = _clamp_0_100(payload.get("confidence"), "confidence")
    top_factors = _normalize_top_factors(payload.get("top_factors"))

    return AssetHealthHighRiskOutput(
        lifecycle_score=lifecycle_score,
        confidence=confidence,
        top_factors=top_factors,
    )


def _build_low_response(payload: Dict[str, Any]) -> AssetHealthLowRiskOutput:
    final_health_score = _clamp_0_100(payload.get("final_health_score"), "final_health_score")
    confidence = _clamp_0_100(payload.get("confidence"), "confidence")
    top_factors = _normalize_top_factors(payload.get("top_factors"))

    raw_status = str(payload.get("final_health_status", "")).strip().upper()
    normalized_status = _status_from_score(final_health_score)

    if raw_status not in ALLOWED_FINAL_STATUS or raw_status != normalized_status:
        final_health_status = normalized_status
    else:
        final_health_status = raw_status

    return AssetHealthLowRiskOutput(
        final_health_status=final_health_status,
        final_health_score=final_health_score,
        confidence=confidence,
        top_factors=top_factors,
    )


def assetHealthService(
    data: AssetHealthInput, health_type: AssetHealthType
) -> Union[AssetHealthHighRiskOutput, AssetHealthLowRiskOutput]:
    logger.info("Generating asset health via LLM (type=%s, asset_uuid=%s)", health_type, data.asset_uuid)

    chain = assetHealthHighRiskChain if health_type == "high" else assetHealthLowRiskChain

    result = chain.invoke({"context_toon": data.context_toon})
    if not isinstance(result, str):
        logger.warning("LLM result is not a string, casting to str")
        result = str(result)

    payload = _extract_json_payload(result)

    if health_type == "high":
        return _build_high_response(payload)

    return _build_low_response(payload)
