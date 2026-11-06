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

def escape_html(text: str) -> str:
    """Escape tag HTML agar aman dikirim ke Telegram parse_mode HTML."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def format_topic_card(idx: int, t: dict) -> list:
    """Format satu kartu topik bersih tanpa angle/hook."""
    lines = []
    cat = t.get("category", "Micro")
    score = t["metrics"]["arbitrage_score"]
    status = t["metrics"]["status"]
    lb = t["metrics"].get("long_benchmark")
    sb = t["metrics"].get("short_benchmark")
    
    lines.append("────────────────────────────")
    lines.append(f"📌 <b>{idx}. {escape_html(t['topic_name'])}</b>")
    lines.append(f"🏷️ <b>Tipe:</b> {cat} Trend | <b>Score:</b> <code>{score}/10</code>")
    lines.append(f"📈 <b>Status Pasar:</b> {status}")
    
    if lb:
        clean_lb_title = escape_html(lb['title'])
        lines.append(f"\n🎬 <b>Bukti Demand Long-Form:</b>\n<a href=\"{lb['url']}\">{clean_lb_title}</a>\n↳ <i>{lb['views']:,} views ({lb['vph']} VPH) • {escape_html(lb['channel'])}</i>")
        
    if sb:
        clean_sb_title = escape_html(sb['title'])
        lines.append(f"\n⚡ <b>Bukti Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{clean_sb_title}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}</i>\n")
    else:
        lines.append("")
        
    return lines

def run_pipeline():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    yt_key = os.getenv("YOUTUBE_API_KEY")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("=" * 60)
    print("🔥 LISA TECH TREND INTELLIGENCE PIPELINE (CLEAN EDITION)")
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
    tech_seeds = ["S26 Ultra", "Snapdragon 8 Elite", "ROG Ally", "RTX 5090", "DeepSeek", "iPad M4"]
    for seed in tech_seeds:
        suggestions = get_yt_suggestions(f"{seed} vs")
        for s in suggestions[:3]:
            raw_signals.append(f"{s} (YT Suggest)")
            
    print(f"Total sinyal mentah terkumpul: {len(raw_signals)}")
    
    # Phase 2: Clustering
    print("\n[Phase 2] Lisa lagi ngerangkum topik tech terhangat...")
    topics = extract_and_cluster_topics(raw_signals, gemini_key)
    print(f"Topik tech terpilih: {len(topics)}")
    
    # Phase 3: Supply-Demand Arbitrage
    print("\n[Phase 3] Mengambil benchmark kredibel (Bahasa Indo/Inggris, no gimmick)...")
    evaluated_topics = []
    for idx, item in enumerate(topics, 1):
        query = item.get("yt_query") or item.get("topic_name")
        print(f"[{idx}/{len(topics)}] Cek pasar YouTube: {query}...")
        metrics = evaluate_topic_supply_demand(query, yt_key)
        evaluated_topics.append({
            **item,
            "metrics": metrics
        })
        
    # Phase 4: Format Message
    print("\n[Phase 4] Menyusun laporan bersih...")
    now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M WIB")
    
    msg_lines = [
        "✨ <b>Pagi Tam! Contekan Tren Hari Ini dari Lisa</b> ✨",
        f"<i>Update: {now_str}</i>\n",
        "Berikut kurasi topik tech terpanas pagi ini dengan bukti demand video valid (Bahasa Indo/Inggris):\n"
    ]
    
    for i, t in enumerate(evaluated_topics, 1):
        msg_lines.extend(format_topic_card(i, t))
            
    msg_lines.append("────────────────────────────")
    msg_lines.append("Kalo lo mau telaah topik spesifik (misal: <i>\"Lis, kalo droiddeck gimana?\"</i>), langsung ketik aja di chat ini yaa Tam! Nanti gue risetin demand pasarnya buat lo. ✨")
    
    report_text = "\n".join(msg_lines)
    
    # Phase 5: Delivery
    if bot_token and chat_id:
        print(f"\nMengirim laporan baru ke Telegram ({chat_id})...")
        sent = send_telegram_message(bot_token, chat_id, report_text)
        if sent:
            print("✅ SUKSES! Laporan bersih berhasil terkirim ke Telegram!")
        else:
            print("❌ GAGAL MENGIRIM KE TELEGRAM.")
    else:
        print("\n[Info] TELEGRAM_CHAT_ID belum diset di .env")

if __name__ == "__main__":
    run_pipeline()
