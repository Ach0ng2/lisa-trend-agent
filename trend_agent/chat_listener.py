import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation.yt_arbitrage import evaluate_topic_supply_demand, escape_html, clean_query_entity
from notifier.telegram_bot import send_telegram_message

TELEGRAM_API_URL = "https://api.telegram.org/bot"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

SIX_CONTENT_PILLARS = [
    {
        "id": "useful_softwares",
        "title": "Useful Softwares & Everyday Apps",
        "desc": "Aplikasi utilitas, problem-solving sehari-hari, transfer file lintas platform, parenting & family tech, serta tools produktivitas.",
        "examples": "LocalSend, Life360, GoodNotes, Raycast, Obsidian, Family Link, Bitwarden, KDE Connect, Syncthing, Arc Browser"
    },
    {
        "id": "handheld_gaming",
        "title": "Handheld & Mobile Gaming",
        "desc": "Handheld PC Windows & SteamOS, emulasi game konsol di Android, aksesoris controller, dan HP gaming bertenaga.",
        "examples": "ROG Ally, Steam Deck, DroidDeck, Ayn Odin 2, RedMagic, Gamesir, emulasi game PC/Switch di mobile"
    },
    {
        "id": "creator_gear",
        "title": "Creator Gear & Audio",
        "desc": "Peralatan produksi konten video, wireless microphone, action camera, kamera vlogging mirrorless, dan audio recording.",
        "examples": "DJI Mic 2, Osmo Pocket 3, Rode Wireless PRO, Sony ZV-E10, Insta360 Ace Pro, Shure SM7dB"
    },
    {
        "id": "smartphones",
        "title": "Smartphones & Flagship Comparisons",
        "desc": "Komparasi smartphone flagship, inovasi kamera zoom, performa chipset harian, dan layar lipat dengan pendekatan objektif.",
        "examples": "Samsung Galaxy S series, Vivo X series, Xiaomi Ultra, iPhone Pro, Pixel"
    },
    {
        "id": "ai_next_gen",
        "title": "AI & Next-Gen Computing",
        "desc": "AI lokal on-device, model open-source, smart glasses, arsitektur GPU baru, dan teknologi masa depan yang aplikatif.",
        "examples": "DeepSeek, Ollama, Ray-Ban Meta, RTX 50 series, Snapdragon X Elite, Claude"
    },
    {
        "id": "productivity_ecosystem",
        "title": "Productivity & Ecosystem Workflow",
        "desc": "Laptop silicon efisien, tablet catatan & multitasking, setup meja kerja terintegrasi, dan fitur ekosistem lintas perangkat.",
        "examples": "MacBook M-series, iPad Mini/Pro, Samsung DeX setup, monitor docking, keyboard mekanikal"
    }
]

CURRENT_PILLAR_INDEX = 0
SEEN_TOPICS_HISTORY = set()

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

DYNAMIC_TOPIC_GEN_PROMPT = """
Kamu adalah Lisa, AI content writer handal untuk channel tech Mas Ario @sheggario dan Tama.
Saat ini kita ingin mencari 3 ide topik baru di Pilar Konten: "{pillar_title}".
Deskripsi Pilar: {pillar_desc}
Contoh acuan tipe konten: {pillar_examples}

ATURAN EKSPLORASI:
1. Contoh acuan di atas HANYA sebagai referensi jenis konten! JANGAN cuma mutar-mutar di contoh tersebut, eksplorasi software atau gadget lain yang sejenis dan relevan!
2. DILARANG KERAS memilih topik atau produk yang sudah pernah disajikan sebelumnya: {seen_history}
3. yt_query HARUS bersih berupa nama murni software/gadget saja (DILARANG menambahkan kata "review", "indonesia", atau "terbaru").
4. DILARANG menggunakan em dash.
5. Kembalikan data dalam format JSON murni:
[
  {{
    "topic_name": "Nama Spesifik Software / Gadget",
    "yt_query": "Query Bersih (contoh: LocalSend, Raycast, Bitwarden)",
    "category": "Micro / Macro / Flash"
  }}
]
"""

def send_chat_action(token: str, chat_id: str, action: str = "typing"):
    """Memberitahu Telegram bahwa Lisa sedang mengetik / mencari data."""
    try:
        requests.post(f"{TELEGRAM_API_URL}{token}/sendChatAction", json={"chat_id": chat_id, "action": action}, timeout=3)
    except Exception:
        pass

def parse_user_intent(user_text: str, gemini_key: str) -> dict:
    url = f"{GEMINI_API_URL}?key={gemini_key}"
    payload = {
        "contents": [{"parts": [{"text": LISA_INTENT_PROMPT.format(user_text=user_text)}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
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
        r = requests.post(url, json=payload, timeout=12)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[Chat Reply Error] {e}")
    return "Iyaa Tam, ada yang bisa gue bantu risetin lagi buat Mas Ario?"

def handle_research_topic(query: str, yt_key: str) -> str:
    clean_q = clean_query_entity(query)
    print(f"[Research] Meneliti topik spesifik: {clean_q}...")
    metrics = evaluate_topic_supply_demand(clean_q, yt_key)
    score = metrics["arbitrage_score"]
    status = metrics["status"]
    lb = metrics.get("long_benchmark")
    sb = metrics.get("short_benchmark")
    
    lines = [
        f"🔍 <b>Hasil Telaah Pasar Lisa: \"{escape_html(clean_q.title())}\"</b>\n",
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

def handle_more_options(gemini_key: str, yt_key: str) -> str:
    global CURRENT_PILLAR_INDEX, SEEN_TOPICS_HISTORY
    
    pillar = SIX_CONTENT_PILLARS[CURRENT_PILLAR_INDEX]
    CURRENT_PILLAR_INDEX = (CURRENT_PILLAR_INDEX + 1) % len(SIX_CONTENT_PILLARS)
    
    print(f"[More Options] Mengeksplorasi Pilar: {pillar['title']} (History seen: {len(SEEN_TOPICS_HISTORY)} items)...")
    
    prompt = DYNAMIC_TOPIC_GEN_PROMPT.format(
        pillar_title=pillar["title"],
        pillar_desc=pillar["desc"],
        pillar_examples=pillar["examples"],
        seen_history=list(SEEN_TOPICS_HISTORY) if SEEN_TOPICS_HISTORY else "Belum ada"
    )
    
    url = f"{GEMINI_API_URL}?key={gemini_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}
    }
    
    candidates = []
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            candidates = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"].strip())
    except Exception as e:
        print(f"[Gemini Dynamic Gen Error] {e}")
        
    if not candidates:
        examples = [e.strip() for e in pillar["examples"].split(",")]
        candidates = [{"topic_name": ex, "yt_query": ex, "category": "Micro"} for ex in examples[:3]]
        
    lines = [
        f"🔄 <b>Opsi Topik Alternatif: {escape_html(pillar['title'])}</b> ✨\n",
        f"<i>Kategori: {pillar['desc']}</i>\n",
        "Ini 3 ide topik baru dengan metrik pasar tervalidasi (Bahasa Indo/Inggris murni):\n"
    ]
    
    for i, item in enumerate(candidates[:3], 1):
        q = clean_query_entity(item.get("yt_query") or item.get("topic_name"))
        cat = item.get("category", "Micro")
        SEEN_TOPICS_HISTORY.add(q.lower())
        
        m = evaluate_topic_supply_demand(q, yt_key)
        lb = m.get("long_benchmark")
        sb = m.get("short_benchmark")
        
        lines.append("────────────────────────────")
        lines.append(f"📌 <b>{i}. {escape_html(item['topic_name'])}</b>")
        lines.append(f"🏷️ <b>Tipe:</b> {cat} Trend | <b>Score:</b> <code>{m['arbitrage_score']}/10</code>")
        lines.append(f"📈 <b>Status Pasar:</b> {m['status']}")
        
        if lb:
            lines.append(f"\n🎬 <b>Demand Long-Form:</b>\n<a href=\"{lb['url']}\">{escape_html(lb['title'])}</a>\n↳ <i>{lb['views']:,} views ({lb['vph']} VPH) • {escape_html(lb['channel'])}</i>")
        if sb:
            lines.append(f"\n⚡ <b>Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{escape_html(sb['title'])}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}\n</i>")
        else:
            lines.append("")
            
    lines.append("────────────────────────────")
    lines.append("Ada yang lebih klik di lo gak Tam dari opsi alternatif di atas? Kalo mau ganti pilar lagi, ketik 'opsi lain' yaa! ✨")
    return "\n".join(lines)

def run_chat_listener():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")
    yt_key = os.getenv("YOUTUBE_API_KEY")
    
    if not token or not gemini_key or not yt_key:
        print("[Error] Kredensial di .env belum lengkap.")
        return
        
    print("=" * 60)
    print("🤖 LISA TELEGRAM CHAT LISTENER (V3 LIGHTNING) IS ONLINE")
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
                        # Kirim status typing instan agar user tahu Lisa aktif bekerja
                        send_chat_action(token, chat_id, "typing")
                        
                        parsed = parse_user_intent(user_text, gemini_key)
                        intent = parsed.get("intent", "GENERAL_CHAT")
                        query = parsed.get("query")
                        print(f"[Intent Parsed] {intent} (Query: {query})")
                        
                        if intent == "RESEARCH_TOPIC" and query:
                            reply = handle_research_topic(query, yt_key)
                        elif intent == "MORE_OPTIONS":
                            reply = handle_more_options(gemini_key, yt_key)
                        else:
                            reply = generate_lisa_chat_reply(user_text, gemini_key)
                            
                        send_telegram_message(token, chat_id, reply)
                        print(f"[Dibalas ke {chat_id}] Sukses!")
                        
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"[Listener Exception] {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_chat_listener()
