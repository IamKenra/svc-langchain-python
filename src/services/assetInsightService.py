import logging

from src.chains.assetInsightChain import assetInsightChain
from src.schemas.assetInsightSchema import AssetInsightInput, AssetInsightOutput

logger = logging.getLogger(__name__)


def assetInsightService(data: AssetInsightInput) -> AssetInsightOutput:
    logger.info("Generating asset insight via LLM")
    logger.info(
        "assetInsightService: context_toon preview: %s",
        (data.context_toon[:200] + "...") if len(data.context_toon) > 200 else data.context_toon,
    )

    try:
        result = assetInsightChain.invoke(
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
