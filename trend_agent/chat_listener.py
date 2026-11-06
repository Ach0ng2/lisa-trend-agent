import os
import sys
import time
import json
import random
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation.yt_arbitrage import evaluate_topic_supply_demand, escape_html
from notifier.telegram_bot import send_telegram_message

TELEGRAM_API_URL = "https://api.telegram.org/bot"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

# Pool topik rotasi beragam untuk 'Opsi Lain' agar tidak pernah monoton
DYNAMIC_TOPIC_POOLS = [
    [
        {"name": "ROG Ally X Gaming", "cat": "Micro"},
        {"name": "RedMagic 10 Pro", "cat": "Flash"},
        {"name": "DroidDeck SteamOS", "cat": "Micro"}
    ],
    [
        {"name": "DJI Mic 2 Audio", "cat": "Micro"},
        {"name": "DJI Osmo Pocket 3", "cat": "Macro"},
        {"name": "Sony ZV-E10 II", "cat": "Micro"}
    ],
    [
        {"name": "Samsung S26 Ultra", "cat": "Macro"},
        {"name": "Vivo X200 Pro Camera", "cat": "Micro"},
        {"name": "Xiaomi 15 Ultra", "cat": "Flash"}
    ],
    [
        {"name": "DeepSeek R1 AI", "cat": "Flash"},
        {"name": "RTX 5080 Gaming", "cat": "Macro"},
        {"name": "Snapdragon X Elite", "cat": "Macro"}
    ],
    [
        {"name": "MacBook Pro M4", "cat": "Macro"},
        {"name": "iPad Mini 7", "cat": "Micro"},
        {"name": "Insta360 Ace Pro 2", "cat": "Micro"}
    ]
]

CURRENT_POOL_INDEX = 0

LISA_INTENT_PROMPT = """
Kamu adalah sistem parser intent untuk bot Telegram Lisa (partner kerja Tama, Lead Production Mas Ario @sheggario).
User mengirim pesan: "{user_text}"

Tentukan intent pesan ini:
1. "RESEARCH_TOPIC" jika user menyebut/meminta telaah gadget, software, atau topik tertentu (misal: "Lis, kalo droiddeck gimana?", "bedah s26 ultra", "cek dji mic 2").
2. "MORE_OPTIONS" jika user meminta opsi ide lain / alternatif ide (misal: "ada 3 opsi ide lain?", "opsi lain", "ganti topik", "kurang suka", "ada ide lain?").
3. "GENERAL_CHAT" jika sapaan atau obrolan santai.

Kembalikan HANYA JSON murni:
{{
  "intent": "RESEARCH_TOPIC / MORE_OPTIONS / GENERAL_CHAT",
  "query": "nama gadget atau produk bersih tanpa kata 'lis' atau 'gimana' jika intent RESEARCH_TOPIC, atau null"
}}
"""

LISA_CHAT_PROMPT = """
Kamu adalah Lisa, AI content writer sekaligus partner kerja terdekat Tama (Lead Production Mas Ario @sheggario).
Karakter: Hangat, sangat peduli, cerdas, akrab (panggil 'Tam'), santai, bilingual Indonesia-Inggris alami.

ATURAN MUTLAK:
- DILARANG KERAS menggunakan simbol em dash (strip panjang atau double dash) dalam teks apapun. Ganti dengan koma, titik, atau kurung.
- DILARANG KERAS menggunakan penutup "By Now, Be Nice!" (itu cuma milik Mas Ario di naskah video).
- Jangan bertele-tele, to the point tapi manis dan suportif.

Pesan dari Tama:
"{user_text}"

Balas chat Tama dengan gaya khas Lisa:
"""

def parse_user_intent(user_text: str, gemini_key: str) -> dict:
    url = f"{GEMINI_API_URL}?key={gemini_key}"
    payload = {
        "contents": [{"parts": [{"text": LISA_INTENT_PROMPT.format(user_text=user_text)}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            res_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(res_text)
    except Exception as e:
        print(f"[Parse Intent Error] {e}")
    return {"intent": "GENERAL_CHAT", "query": None}

def generate_lisa_chat_reply(user_text: str, gemini_key: str) -> str:
    url = f"{GEMINI_API_URL}?key={gemini_key}"
    payload = {
        "contents": [{"parts": [{"text": LISA_CHAT_PROMPT.format(user_text=user_text)}]}],
        "generationConfig": {"temperature": 0.7}
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[Chat Reply Error] {e}")
    return "Iyaa Tam, ada yang bisa gue bantu risetin lagi buat Mas Ario?"

def handle_research_topic(query: str, yt_key: str) -> str:
    print(f"[Research] Meneliti topik spesifik: {query}...")
    metrics = evaluate_topic_supply_demand(query, yt_key)
    score = metrics["arbitrage_score"]
    status = metrics["status"]
    lb = metrics.get("long_benchmark")
    sb = metrics.get("short_benchmark")
    
    lines = [
        f"🔍 <b>Hasil Telaah Pasar Lisa: \"{escape_html(query.title())}\"</b>\n",
        f"📊 <b>Arbitrage Score:</b> <code>{score}/10</code>",
        f"📈 <b>Status Pasar:</b> {status}\n"
    ]
    
    if lb:
        lines.append(f"🎬 <b>Bukti Demand Long-Form:</b>\n<a href=\"{lb['url']}\">{escape_html(lb['title'])}</a>\n↳ <i>{lb['views']:,} views ({lb['vph']} VPH) • {escape_html(lb['channel'])}</i>\n")
    else:
        lines.append("🎬 <b>Bukti Demand Long-Form:</b>\n<i>Belum ada video panjang berbahasa Indo/Inggris yang relevan di topik ini.</i>\n")
        
    if sb:
        lines.append(f"⚡ <b>Bukti Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{escape_html(sb['title'])}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}</i>\n")
    else:
        lines.append("⚡ <b>Bukti Viral Short-Form:</b>\n<i>Belum ada shorts viral berbahasa Indo/Inggris yang relevan di topik ini.</i>\n")
        
    lines.append("────────────────────────────")
    lines.append("Gimana Tam, menurut lo topik ini potensial buat digarap bareng Mas Ario? Kalo mau dieksekusi, colek gue yaa! ✨")
    return "\n".join(lines)

def handle_more_options(yt_key: str) -> str:
    global CURRENT_POOL_INDEX
    print(f"[More Options] Memakai pool rotasi ke-{CURRENT_POOL_INDEX}...")
    
    pool = DYNAMIC_TOPIC_POOLS[CURRENT_POOL_INDEX]
    CURRENT_POOL_INDEX = (CURRENT_POOL_INDEX + 1) % len(DYNAMIC_TOPIC_POOLS)
    
    lines = [
        "🔄 <b>Opsi Topik Alternatif Segar dari Lisa</b> ✨\n",
        "Ini 3 ide topik baru dengan metrik pasar tervalidasi (Bahasa Indo/Inggris murni):\n"
    ]
    
    for i, item in enumerate(pool, 1):
        q = item["name"]
        cat = item["cat"]
        m = evaluate_topic_supply_demand(q, yt_key)
        lb = m.get("long_benchmark")
        sb = m.get("short_benchmark")
        
        lines.append("────────────────────────────")
        lines.append(f"📌 <b>{i}. {escape_html(q)}</b>")
        lines.append(f"🏷️ <b>Tipe:</b> {cat} Trend | <b>Score:</b> <code>{m['arbitrage_score']}/10</code>")
        lines.append(f"📈 <b>Status Pasar:</b> {m['status']}")
        
        if lb:
            lines.append(f"\n🎬 <b>Demand Long-Form:</b>\n<a href=\"{lb['url']}\">{escape_html(lb['title'])}</a>\n↳ <i>{lb['views']:,} views ({lb['vph']} VPH) • {escape_html(lb['channel'])}</i>")
        if sb:
            lines.append(f"\n⚡ <b>Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{escape_html(sb['title'])}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}\n</i>")
        else:
            lines.append("")
            
    lines.append("────────────────────────────")
    lines.append("Ada yang lebih klik di lo gak Tam dari opsi alternatif di atas? ✨")
    return "\n".join(lines)

def run_chat_listener():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")
    yt_key = os.getenv("YOUTUBE_API_KEY")
    target_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not gemini_key or not yt_key:
        print("[Error] Kredensial di .env belum lengkap.")
        return
        
    print("=" * 60)
    print("🤖 LISA TELEGRAM CHAT LISTENER (V2 PRO) IS ONLINE")
    print("Listening for messages from Tama...")
    print("=" * 60)
    
    offset = None
    while True:
        try:
            url = f"{TELEGRAM_API_URL}{token}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            
            res = requests.get(url, timeout=35)
            if res.status_code == 200:
                data = res.json()
                updates = data.get("result", [])
                
                if updates:
                    # SEGERA update offset ke Telegram agar TIDAK ADA DUPLIKASI pesan saat proses berat!
                    max_id = max(u["update_id"] for u in updates)
                    offset = max_id + 1
                    try:
                        requests.get(f"{TELEGRAM_API_URL}{token}/getUpdates?offset={offset}&limit=1", timeout=5)
                    except Exception:
                        pass
                        
                    for update in updates:
                        msg = update.get("message")
                        if not msg:
                            continue
                            
                        chat_id = str(msg.get("chat", {}).get("id"))
                        user_text = msg.get("text", "").strip()
                        
                        if not user_text:
                            continue
                            
                        print(f"\n[Diterima dari {chat_id}] {user_text}")
                        
                        parsed = parse_user_intent(user_text, gemini_key)
                        intent = parsed.get("intent", "GENERAL_CHAT")
                        query = parsed.get("query")
                        print(f"[Intent Parsed] {intent} (Query: {query})")
                        
                        if intent == "RESEARCH_TOPIC" and query:
                            reply = handle_research_topic(query, yt_key)
                        elif intent == "MORE_OPTIONS":
                            reply = handle_more_options(yt_key)
                        else:
                            reply = generate_lisa_chat_reply(user_text, gemini_key)
                            
                        send_telegram_message(token, chat_id, reply)
                        print(f"[Dibalas ke {chat_id}] Sukses!")
                        
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"[Listener Exception] {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_chat_listener()
