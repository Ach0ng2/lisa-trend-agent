import os
import sys
import datetime
from dotenv import load_dotenv

# Pastikan console Windows support karakter UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Tambahkan path root agar modul lokal terbaca
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.trends_rss import fetch_google_trends_rss
from ingestion.yt_suggest import get_yt_suggestions
from clustering.topic_cluster import extract_and_cluster_topics
from evaluation.yt_arbitrage import evaluate_topic_supply_demand
from notifier.telegram_bot import send_telegram_message

def run_pipeline():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    yt_key = os.getenv("YOUTUBE_API_KEY")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("=" * 60)
    print("🔥 LISA TECH TREND INTELLIGENCE PIPELINE (LISA VOICE EDITION)")
    print("=" * 60)
    
    if not gemini_key or not yt_key:
        print("[Error] GEMINI_API_KEY atau YOUTUBE_API_KEY belum diset di .env")
        return
        
    # Phase 1: Ingestion
    print("\n[Phase 1] Lisa lagi narik sinyal tren mentah...")
    trends_id = fetch_google_trends_rss("ID")
    trends_us = fetch_google_trends_rss("US")
    
    raw_signals = []
    for t in trends_id:
        raw_signals.append(f"{t['title']} (Google Trends ID: {t['traffic']})")
    for t in trends_us[:15]:
        raw_signals.append(f"{t['title']} (Google Trends US: {t['traffic']})")
        
    # Seed gadget terkini untuk autocomplete
    tech_seeds = ["S26 Ultra", "Snapdragon 8 Elite", "ROG Ally", "RTX 5090", "DeepSeek", "iPad M4", "Dimensity 9400"]
    for seed in tech_seeds:
        suggestions = get_yt_suggestions(f"{seed} vs")
        for s in suggestions[:3]:
            raw_signals.append(f"{s} (YT Suggest)")
            
    print(f"Total sinyal mentah terkumpul: {len(raw_signals)}")
    
    # Phase 2: Clustering & Entity Extraction via Gemini Flash Lite
    print("\n[Phase 2] Lisa lagi ngerangkum topik & ngeracik angle cerita...")
    topics = extract_and_cluster_topics(raw_signals, gemini_key)
    print(f"Topik tech terpilih: {len(topics)}")
    
    # Phase 3: Supply-Demand Arbitrage via YouTube Data API
    print("\n[Phase 3] Menghitung Arbitrage Index & View Velocity di YouTube...")
    evaluated_topics = []
    for idx, item in enumerate(topics, 1):
        query = item.get("yt_query") or item.get("topic_name")
        print(f"[{idx}/{len(topics)}] Cek pasar YouTube: {query}...")
        metrics = evaluate_topic_supply_demand(query, yt_key)
        
        evaluated_topics.append({
            **item,
            "metrics": metrics
        })
        
    # Phase 4: Format Message in Lisa's Authentic Voice
    print("\n[Phase 4] Menyusun pesan cantik khas gaya obrolan Lisa...")
    now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M WIB")
    
    msg_lines = [
        "✨ <b>Pagi Tam! Contekan Tren Hari Ini dari Lisa</b> ✨",
        f"<i>Update: {now_str}</i>\n",
        "Gue udah saringin topik-topik tech yang momentumnya lagi kenceng banget pagi ini. Ada yang supply-nya masih sepi di YouTube, pas banget buat lo bahas bareng Mas Ario!\n"
    ]
    
    for i, t in enumerate(evaluated_topics, 1):
        cat = t.get("category", "Micro")
        score = t["metrics"]["arbitrage_score"]
        vph = t["metrics"]["avg_vph"]
        status = t["metrics"]["status"]
        format_rec = t.get("recommended_format", "IG Reels / YouTube")
        
        msg_lines.append("────────────────────────────")
        msg_lines.append(f"📌 <b>{i}. {t['topic_name']}</b>")
        msg_lines.append(f"🏷️ <b>Klasifikasi:</b> {cat} Trend")
        msg_lines.append(f"🎯 <b>Format Cocok:</b> <b>{format_rec}</b>")
        msg_lines.append(f"📊 <b>Arbitrage Index:</b> <code>{score}/10</code> ({status})")
        msg_lines.append(f"⚡ <b>Kecepatan Views:</b> ~{vph} Views/Jam")
        msg_lines.append(f"\n💡 <b>Catatan Angle Lisa:</b>\n<i>\"{t.get('angle_idea')}\"</i>")
        
        # Contoh video pembanding
        top_v = t["metrics"].get("top_recent_videos")
        if top_v and len(top_v) > 0:
            sample = top_v[0]
            clean_title = sample['title'].replace("<", "&lt;").replace(">", "&gt;")
            msg_lines.append(f"\n🎬 <b>Intip Video Kompetitor:</b>\n<a href=\"{sample['url']}\">{clean_title}</a> (~{sample['vph']} VPH)\n")
        else:
            msg_lines.append("")
            
    msg_lines.append("────────────────────────────")
    msg_lines.append("Kalo ada angle yang klik di lo, kabarin gue di chat yaa biar langsung gue bantu bikin draft naskahnya bareng tim produksi!")
    msg_lines.append("Semangat produksinya hari ini Tam! 💪✨\n")
    msg_lines.append("<i>By Now, Be Nice! ✨</i>")
    
    report_text = "\n".join(msg_lines)
    
    # Phase 5: Delivery
    if bot_token and chat_id:
        print(f"\nMengirim pesan baru ke Telegram ({chat_id})...")
        sent = send_telegram_message(bot_token, chat_id, report_text)
        if sent:
            print("✅ SUKSES! Pesan gaya Lisa berhasil mendarat di Telegram!")
        else:
            print("❌ GAGAL MENGIRIM KE TELEGRAM.")
    else:
        print("\n[Info] TELEGRAM_CHAT_ID belum diset di .env")

if __name__ == "__main__":
    run_pipeline()
