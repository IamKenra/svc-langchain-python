from src.models.llm_client import llm_client
import logging
import json
import re

logger = logging.getLogger(__name__)

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL) 
    if match:
        return match.group(0)  
    return None

def generate_recommendation(data):
    prompt = f"""
    Berikut adalah statistik rata-rata performa server pada hari ini:
    - CPU Usage: {data.cpu_usage}%
    - RAM Usage: {data.ram_usage}%
    - Disk Usage: {data.disk_usage}%

    Berdasarkan statistik di atas, lakukan rekomendasi untuk mengoptimalkan performa server atau server sudah berjalan optimal.
    Anda cukup menganalisa query ini saja tidak perlu melihat data sebelumnya.
    Cukup highlight bagian yang perlu diperhatikan saja, conntoh jika cpu load saja yamg tinggi cukup highlight cpu load saja.
    Jika load server termasuk optimal maka cukup berikan balikan bahwa server sudah berjalan optimal.
    Berikan rekomendasi dalam format JSON berikut **tanpa tambahan teks lain**:
    ```json
    {{
        "recommendations": [
            {{
                "title": "Judul Rekomendasi",
                "description": "Deskripsi lengkap rekomendasi"
            }}
        ],
        "summary": "Ringkasan rekomendasi untuk ditampilkan di notifikasi"
    }}
    ```
    **Ingat:** Hanya keluarkan JSON tanpa tambahan teks lain. Cukup berikan rekomendasi berdasarkan statistik yang diberikan tidak perlu melakuka reasoning tambahan.
    """

    logger.info(f"🔍 Generating recommendation using hosted Ollama API...")
    response = llm_client.predict(prompt).strip()
    
    #ekstrak JSON dari teks
    json_text = extract_json(response)

    if json_text:
        try:
            formatted_response = json.loads(json_text)  
            return formatted_response  
        except json.JSONDecodeError as e:
            logger.error(f"JSON Error: {e}")
    
    logger.error(" LLM output is not a valid JSON. Raw Output: " + response)
    return {
        "recommendations": [{"title": "Error", "description": "LLM tidak mengembalikan format JSON yang valid."}],
        "summary": "Terjadi kesalahan dalam memproses rekomendasi."
    }
