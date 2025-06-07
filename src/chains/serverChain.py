from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from src.clients.llm_client import llm_client
from src.schemas.serverSchema import RecommendationResponse

parser = PydanticOutputParser(pydantic_object=RecommendationResponse)

recommendation_prompt_template = PromptTemplate(
    template="""
Statistik rata-rata performa server saat ini:
- Penggunaan CPU: {cpu}%
- Penggunaan RAM: {ram}%
- Penggunaan Disk: {disk}%

Bayangkan anda adalah seorang ahli dalam mengelola inventaris IT di sebuah perusahaan besar. Berdasarkan data statistik diatas,
jabarkan kondisi server saat ini. Berikan rekomendasi menggunakan bahasa indonesia yang baik dan benar.
Pastikan setiap respon anda selalu **KONSISTEN SETIAP KALIMAT DAN KATA**.
Anda cukup menganalisa pesan yang ini saja tidak perlu melihat pesan sebelumnya karena ini respon anda bersifat sekali pakai.
{format_instructions}
""",
    input_variables=["cpu", "ram", "disk"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

server_chain = recommendation_prompt_template | llm_client | parser
