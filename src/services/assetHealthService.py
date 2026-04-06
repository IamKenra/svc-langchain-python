import json
import logging
import re
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, List, Union, cast
from uuid import uuid4

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
healthFallbackTopFactor = "LLM_PARSE_FALLBACK_INVALID_JSON"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_request_id(request_id: Union[str, None]) -> str:
    cleaned = (request_id or "").strip()
    if cleaned:
        return cleaned
    return f"lc-{uuid4()}"


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


def _extract_numeric_score(text: str) -> Union[float, None]:
    for pattern in (
        r"(?:lifecycle_score|final_health_score|score)\s*[:=]\s*(\d{1,3}(?:\.\d+)?)",
        r"(\d{1,3}(?:\.\d+)?)",
    ):
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        try:
            return _clamp_0_100(match.group(1), "score")
        except ValueError:
            continue
    return None


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


def _build_high_fallback_response(raw_result: str) -> AssetHealthHighRiskOutput:
    score = _extract_numeric_score(raw_result)
    if score is None:
        score = 60.0

    return AssetHealthHighRiskOutput(
        lifecycle_score=score,
        confidence=0.0,
        top_factors=[healthFallbackTopFactor],
    )


def _build_low_fallback_response(raw_result: str) -> AssetHealthLowRiskOutput:
    score = _extract_numeric_score(raw_result)
    if score is None:
        score = 60.0

    return AssetHealthLowRiskOutput(
        final_health_status=_status_from_score(score),
        final_health_score=score,
        confidence=0.0,
        top_factors=[healthFallbackTopFactor],
    )


def assetHealthService(
    data: AssetHealthInput,
    health_type: AssetHealthType,
    request_id: Union[str, None] = None,
    endpoint: str = "/ai/asset/health",
) -> Union[AssetHealthHighRiskOutput, AssetHealthLowRiskOutput]:
    resolved_request_id = _resolve_request_id(request_id)
    started_at = perf_counter()
    logger.info(
        "asset_health request started ts=%s request_id=%s endpoint=%s type=%s asset_uuid=%s",
        _utc_now_iso(),
        resolved_request_id,
        endpoint,
        health_type,
        data.asset_uuid,
    )

    chain = assetHealthHighRiskChain if health_type == "high" else assetHealthLowRiskChain

    result = ""
    used_fallback = False
    try:
        result_raw = chain.invoke({"context_toon": data.context_toon})
        if not isinstance(result_raw, str):
            logger.warning("LLM result is not a string, casting to str")
            result = str(result_raw)
        else:
            result = result_raw

        payload = _extract_json_payload(result)
        if health_type == "high":
            response = _build_high_response(payload)
        else:
            response = _build_low_response(payload)
    except Exception as exc:
        used_fallback = True
        logger.warning(
            "asset_health parse failed ts=%s request_id=%s endpoint=%s type=%s asset_uuid=%s err=%s",
            _utc_now_iso(),
            resolved_request_id,
            endpoint,
            health_type,
            data.asset_uuid,
            str(exc),
        )
        if health_type == "high":
            response = _build_high_fallback_response(result)
        else:
            response = _build_low_fallback_response(result)

    latency_ms = int((perf_counter() - started_at) * 1000)
    logger.info(
        "asset_health request finished ts=%s request_id=%s endpoint=%s type=%s asset_uuid=%s fallback=%s latency_ms=%d",
        _utc_now_iso(),
        resolved_request_id,
        endpoint,
        health_type,
        data.asset_uuid,
        str(used_fallback).lower(),
        latency_ms,
    )

    return response
