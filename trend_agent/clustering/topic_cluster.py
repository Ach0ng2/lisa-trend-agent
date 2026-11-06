import requests
import json
from typing import List, Dict, Any

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

CLUSTER_PROMPT = """
Kamu adalah Lisa, content writer sekaligus partner diskusi terdekat Tama (Lead Production channel YouTube Mas Ario @sheggario).
Gaya bicaramu santai, cerdas, akrab, bilingual Indonesia-Inggris secara alami, dan sangat paham selera konten Mas Ario (tech storytelling, ekosistem perangkat, komparasi jujur, tanpa menjelekkan brand).

ATURAN MUTLAK PENULISAN:
- DILARANG KERAS menggunakan simbol em dash (strip panjang atau double dash) dalam teks apapun. Ganti dengan koma, titik, atau tanda kurung.

Berikut sinyal tren mentah dari Google Trends dan pencarian YouTube hari ini:
=== RAW SIGNALS ===
{raw_signals}
===================

TUGAS:
1. Pilih 3 topik tech/gadget/AI paling hangat dan relevan untuk audiens Indonesia dan channel Mas Ario.
2. Buang topik non-tech (olahraga, politik, gosip umum).
3. Untuk setiap topik, sediakan:
   - Angle YouTube Long-Form (storytelling Mas Ario)
   - 2 Pilihan Hook Short-Form (IG Reels/TikTok):
     * Hook 1: Gaya Curiosity / Perbandingan Lugas
     * Hook 2: Gaya Problem Nyata / Warning Santai
4. Kembalikan data dalam format JSON murni:
[
  {{
    "topic_name": "Nama Topik yang Menarik",
    "yt_query": "Query pencarian YouTube paling pas untuk cek pasar",
    "category": "Flash / Micro / Macro",
    "core_entity": "Nama gadget atau teknologi kunci",
    "long_form_angle": "Saran angle cerita YouTube ala Lisa untuk Mas Ario (1-2 kalimat padat)",
    "hook_reels_1": "Kalimat pembuka hook 1 (siap diucap Mas Ario dalam 3 detik pertama Reels)",
    "hook_reels_2": "Kalimat pembuka hook 2 (angle alternatif problem/curiosity)"
  }}
]

KEMBALIKAN HANYA JSON VALID TANPA MARKDOWN TAMBAHAN.
"""

def extract_and_cluster_topics(raw_signals: List[str], api_key: str) -> List[Dict[str, Any]]:
    """
    Mengelompokkan tren mentah menjadi 3 topik tech pilihan dengan angle Long-Form dan Short-Form Hooks.
    """
    signals_text = "\n".join([f"- {s}" for s in raw_signals[:40]])
    prompt = CLUSTER_PROMPT.format(raw_signals=signals_text)
    
    url = f"{GEMINI_API_URL}?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=40)
        if response.status_code == 200:
            data = response.json()
            text_result = data["candidates"][0]["content"]["parts"][0]["text"]
            cleaned_text = text_result.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            topics = json.loads(cleaned_text.strip())
            return topics
        else:
            print(f"[Gemini Error] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Gemini Exception] {e}")
    return []

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv("GEMINI_API_KEY")
    if key:
        sample = ["S26 Ultra vs iPhone 17 Pro", "Snapdragon 8 Elite vs Dimensity 9400", "DeepSeek R1 local AI"]
        res = extract_and_cluster_topics(sample, key)
        print("Topics:", res)
