from src.chains.serverChain import server_chain
from src.schemas.serverSchema import ServerStatusInput, RecommendationResponse
import logging

logger = logging.getLogger(__name__)

def generate_server_recommendation(data: ServerStatusInput) -> dict:
    logger.info("Generating recommendation via LLM")

    try:
        result: RecommendationResponse = server_chain.invoke({
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
