from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from src.clients.llm_client import llm_client
from src.schemas.serverSchema import ServerStatusRightNow

ParserStatusRightNow = PydanticOutputParser(pydantic_object=ServerStatusRightNow)

StatusRightNowTemplate = PromptTemplate(
    template="""
    Statistik rata-rata performa server saat ini:
    - Penggunaan CPU: {cpu}%
    - Penggunaan RAM: {ram}%
    - Penggunaan Disk: {disk}%

    Anda adalah seorang ahli dalam mengelola inventaris IT di sebuah perusahaan besar. Berdasarkan data statistik diatas,
    lakukan analisa mendalam dan jabarkan kondisi server saat ini. Berikan rekomendasi SECARA SINGKAT DAN INSIGHTFULL menggunakan bahasa indonesia yang baik dan benar.
    Contoh Kondisi yang bisa diberikan adalah:
    - Kondisi server saat ini baik, tidak ada masalah yang perlu diperhatikan.
    - Kondisi server saat ini perlu perhatian pada penggunaan CPU yang tinggi.
    - Kondisi server saat ini perlu pemantauan dan perhatian pada penggunaan CPU,RAM yang tinggi.
    Pastikan setiap respon anda selalu **KONSISTEN SETIAP KALIMAT DAN KATA**.
    Anda cukup menganalisa pesan yang ini saja tidak perlu melihat pesan sebelumnya karena ini respon anda bersifat sekali pakai.
    {format_instructions}
    """,
    input_variables=["cpu", "ram", "disk"],
    partial_variables={"format_instructions": ParserStatusRightNow.get_format_instructions()}
)

StatusRightNow = StatusRightNowTemplate | llm_client | ParserStatusRightNow
