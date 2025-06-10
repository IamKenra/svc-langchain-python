from src.chains.deviceChain import *
from src.schemas.deviceSchema import *
import logging

logger = logging.getLogger(__name__)

def deviceRecomendationService(data: deviceRecomendationInput) -> dict:
    logger.info("Generating recommendation via LLM")

    try:
        formatted_device_list = "\n".join(
            [f"- {device.device_model} (ID: {device.device_id}, Spesifikasi: {device.spesification}, Status: {device.status})"
             for device in data.device_list]
        )

        result: deviceRecomendationRespone = deviceRecomendation.invoke({
            "role_position": data.role_position,
            "device_list": formatted_device_list,
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
