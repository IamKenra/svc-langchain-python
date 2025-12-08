from src.chains.assignChain import assignRecommendation
from src.schemas.assignSchema import AssignRecommendationInput
import logging

logger = logging.getLogger(__name__)


def assignRecommendationService(data: AssignRecommendationInput) -> str:
    logger.info("Generating assign recommendation via LLM")

    try:
        result = assignRecommendation.invoke(
            {
                "employee_profile_toon": data.employee_profile_toon,
                "current_devices_toon": data.current_devices_toon,
                "available_devices_toon": data.available_devices_toon,
                "max_recommendations": data.max_recommendations,
            }
        )

        # llm_client mengembalikan string langsung
        if not isinstance(result, str):
            logger.warning("LLM result is not a string, casting to str")
            result = str(result)

        logger.info("LLM assign recommendation generated successfully")
        return result.strip()

    except Exception as e:
        logger.error(f"Unexpected error in assignRecommendationService: {e}")
        raise

