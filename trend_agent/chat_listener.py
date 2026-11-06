import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluation.yt_arbitrage import evaluate_topic_supply_demand
from notifier.telegram_bot import send_telegram_message
from ingestion.trends_rss import fetch_google_trends_rss
from ingestion.yt_suggest import get_yt_suggestions
from clustering.topic_cluster import extract_and_cluster_topics

def escape_html(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

TELEGRAM_API_URL = "https://api.telegram.org/bot"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"

LISA_INTENT_PROMPT = """
Kamu adalah sistem parser intent untuk asisten Lisa di Telegram (partner kerja Tama, Lead Production Mas Ario @sheggario).
User mengirim pesan: "{user_text}"

Tentukan intent pesan ini:
1. "RESEARCH_TOPIC" jika user meminta riset/telaah gadget, software, atau topik tertentu (misal: "Lis, kalo droiddeck gimana?", "bedah poco f9", "cek DJI mic").
2. "MORE_OPTIONS" jika user meminta ide/opsi topik lain (misal: "opsi lain dong", "kurang suka", "ganti topik", "ada ide lain?").
3. "GENERAL_CHAT" jika sapaan, obrolan santai, atau diskusi biasa.

Kembalikan HANYA JSON murni:
{{
  "intent": "RESEARCH_TOPIC / MORE_OPTIONS / GENERAL_CHAT",
  "query": "kata kunci pencarian bersih jika intent RESEARCH_TOPIC, atau null"
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
        lines.append("🎬 <b>Bukti Demand Long-Form:</b>\n<i>Belum ada video panjang besar di niche ini (peluang first-mover).</i>\n")
        
    if sb:
        lines.append(f"⚡ <b>Bukti Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{escape_html(sb['title'])}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}</i>\n")
    else:
        lines.append("⚡ <b>Bukti Viral Short-Form:</b>\n<i>Belum ada shorts viral yang meledak di topik ini.</i>\n")
        
    lines.append("────────────────────────────")
    lines.append("Gimana Tam, menurut lo topik ini menarik buat dieksekusi bareng Mas Ario? Kalo mau naskahnya, kabarin gue yaa! ✨")
    return "\n".join(lines)

def handle_more_options(gemini_key: str, yt_key: str) -> str:
    print("[More Options] Mencari 3 topik alternatif segar...")
    # Tarik seed segar
    alt_seeds = ["MacBook M4", "Insta360 Ace Pro", "DJI Mic 2", "Ollama", "iPad Mini 7", "Anker PowerBank"]
    raw = []
    for s in alt_seeds:
        for sug in get_yt_suggestions(f"{s} review")[:2]:
            raw.append(f"{sug} (YT Suggest)")
    topics = extract_and_cluster_topics(raw, gemini_key)
    
    lines = [
        "🔄 <b>Opsi Topik Alternatif Segar dari Lisa</b> ✨\n",
        "Ini 3 ide topik baru dengan metrik pasar tervalidasi (Bahasa Indo/Inggris murni):\n"
    ]
    for i, t in enumerate(topics[:3], 1):
        q = t.get("yt_query") or t.get("topic_name")
        m = evaluate_topic_supply_demand(q, yt_key)
        cat = t.get("category", "Micro")
        lb = m.get("long_benchmark")
        sb = m.get("short_benchmark")
        
        lines.append("────────────────────────────")
        lines.append(f"📌 <b>{i}. {escape_html(t['topic_name'])}</b>")
        lines.append(f"🏷️ <b>Tipe:</b> {cat} Trend | <b>Score:</b> <code>{m['arbitrage_score']}/10</code>")
        lines.append(f"📈 <b>Status Pasar:</b> {m['status']}")
        if lb:
            lines.append(f"\n🎬 <b>Demand Long-Form:</b> <a href=\"{lb['url']}\">{escape_html(lb['title'])}</a> ({lb['views']:,} views • {escape_html(lb['channel'])})")
        if sb:
            lines.append(f"\n⚡ <b>Viral Short-Form:</b> <a href=\"{sb['url']}\">{escape_html(sb['title'])}</a> ({sb['views']:,} views • {escape_html(sb['channel'])})\n")
            
    lines.append("────────────────────────────")
    lines.append("Ada yang lebih klik di lo gak Tam dari opsi di atas? ✨")
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
    print("🤖 LISA TELEGRAM CHAT LISTENER IS ONLINE")
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
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message")
                    if not msg:
                        continue
                        
                    chat_id = str(msg.get("chat", {}).get("id"))
                    user_text = msg.get("text", "").strip()
                    
                    if not user_text:
                        continue
                        
                    print(f"\n[Diterima dari {chat_id}] {user_text}")
                    
                    # Cek intent
                    parsed = parse_user_intent(user_text, gemini_key)
                    intent = parsed.get("intent", "GENERAL_CHAT")
                    query = parsed.get("query")
                    
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
            time.sleep(3)

if __name__ == "__main__":
    run_chat_listener()
