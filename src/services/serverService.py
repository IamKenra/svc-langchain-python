from src.chains.serverChain import StatusRightNow
from src.schemas.serverSchema import ServerStatusInput, ServerStatusRightNow
import logging

logger = logging.getLogger(__name__)

def RightNowCondition(data: ServerStatusInput) -> dict:
    logger.info("Generating recommendation via LLM")

    try:
        result: ServerStatusRightNow = StatusRightNow.invoke({
            "cpu": data.cpu,
            "ram": data.ram,
            "disk": data.disk
        })

        logger.info("LLM output parsed successfully")
        return result.model_dump()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "recommendations": [
                {
                    "title": "Terjadi Kesalahan",
                    "description": "Tidak dapat memproses rekomendasi dari LLM."
                }
            ],
            "summary": "Gagal mendapatkan rekomendasi dari model."
        }
