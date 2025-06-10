from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from src.clients.llm_client import llm_client
from src.schemas.deviceSchema import *

parserDeviceRecomendation = PydanticOutputParser(pydantic_object=deviceRecomendationRespone)

deviceRecomendationTemplate = PromptTemplate(
    template="""
    Anda adalah seorang ahli dalam mengelola inventaris IT di sebuah perusahaan besar.
    Berikan rekomendasi perangkat yang sesuai dengan posisi {role_position} 
    berdasarkan daftar perangkat yang tersedia:
    {device_list}

    Pastikan rekomendasi yang diberikan sesuai dengan kebutuhan posisi tersebut.
    Tujuan utamanya adalah memberikan rekomendasi perangkat yang tepat dan relevan untuk posisi tersebut sesuai dengan inventaris yang tersedia.

    Rekomendasi harus memenuh beberapa kriteria berikut:
    - Rekomendasi harus sesuai dengan kebutuhan yang diberikan.
    - Rekomendasi harus mempertimbagkan efisiensi dan efektivitas perangkat, tidak overspec ataupun underspec.
    - Rekomendasi tidak memerlukan perangkat dengan usia terbaru atau spesifikasi tinggi jika tidak diperlukan.

    Gunakan bahasa indonesia yang baik dan benar.
    Pastikan setiap respon anda selalu **KONSISTEN SETIAP KALIMAT DAN KATA**.
    Anda cukup menganalisa pesan yang ini saja tidak perlu melihat pesan sebelumnya karena ini respon anda bersifat sekali pakai.
    {format_instructions}
    """,
    input_variables=["position", "device_list"],
    partial_variables={"format_instructions": parserDeviceRecomendation.get_format_instructions()}
)

deviceRecomendation = deviceRecomendationTemplate | llm_client | parserDeviceRecomendation
