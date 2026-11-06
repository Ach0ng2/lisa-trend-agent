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

def run_pipeline():
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    yt_key = os.getenv("YOUTUBE_API_KEY")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("=" * 60)
    print("🔥 LISA TECH TREND INTELLIGENCE PIPELINE (PRO BENCHMARKS EDITION)")
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
    
    # Phase 2: Clustering & Entity Extraction via Gemini Flash Lite
    print("\n[Phase 2] Lisa lagi ngeracik topik, angle YouTube, dan hook Reels...")
    topics = extract_and_cluster_topics(raw_signals, gemini_key)
    print(f"Topik tech terpilih: {len(topics)}")
    
    # Phase 3: Supply-Demand Arbitrage & Kredibel Benchmarking
    print("\n[Phase 3] Mengambil benchmark kredibel (Long-Form & Shorts viral)...")
    evaluated_topics = []
    for idx, item in enumerate(topics, 1):
        query = item.get("yt_query") or item.get("topic_name")
        print(f"[{idx}/{len(topics)}] Cek traffic valid YouTube: {query}...")
        metrics = evaluate_topic_supply_demand(query, yt_key)
        evaluated_topics.append({
            **item,
            "metrics": metrics
        })
        
    # Phase 4: Format Message in Lisa's Authentic Voice
    print("\n[Phase 4] Menyusun laporan dengan benchmark ratusan ribu views...")
    now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M WIB")
    
    msg_lines = [
        "✨ <b>Pagi Tam! Contekan Tren Hari Ini dari Lisa</b> ✨",
        f"<i>Update: {now_str}</i>\n",
        "Filternya udah gue upgrade yaa! Sekarang video pembandingnya cuma ngambil yang <b>terbukti meledak (views puluhan ribu sampai jutaan)</b>, plus gue kasih <b>opsi Hook buat Reels / TikTok</b>!\n"
    ]
    
    for i, t in enumerate(evaluated_topics, 1):
        cat = t.get("category", "Micro")
        score = t["metrics"]["arbitrage_score"]
        status = t["metrics"]["status"]
        lb = t["metrics"].get("long_benchmark")
        sb = t["metrics"].get("short_benchmark")
        
        msg_lines.append("────────────────────────────")
        msg_lines.append(f"📌 <b>{i}. {escape_html(t['topic_name'])}</b>")
        msg_lines.append(f"🏷️ <b>Tipe:</b> {cat} Trend | <b>Score:</b> <code>{score}/10</code>")
        msg_lines.append(f"📈 <b>Status Pasar:</b> {status}")
        
        # Angle Long-form
        long_angle = t.get("long_form_angle") or t.get("angle_idea", "")
        msg_lines.append(f"\n💡 <b>Angle YouTube (Long-Form):</b>\n<i>\"{escape_html(long_angle)}\"</i>")
        
        # Hook Reels / TikTok
        hook1 = t.get("hook_reels_1", "")
        hook2 = t.get("hook_reels_2", "")
        if hook1 or hook2:
            msg_lines.append(f"\n📱 <b>Opsi Hook Reels/Shorts Mas Ario:</b>")
            if hook1:
                msg_lines.append(f"• <i>\"{escape_html(hook1)}\"</i>")
            if hook2:
                msg_lines.append(f"• <i>\"{escape_html(hook2)}\"</i>")
                
        # Benchmark Videos
        if lb:
            clean_lb_title = escape_html(lb['title'])
            msg_lines.append(f"\n🎬 <b>Bukti Demand Long-Form:</b>\n<a href=\"{lb['url']}\">{clean_lb_title}</a>\n↳ <i>{lb['views']:,} views ({lb['vph']} VPH) • {escape_html(lb['channel'])}</i>")
            
        if sb:
            clean_sb_title = escape_html(sb['title'])
            msg_lines.append(f"\n⚡ <b>Bukti Viral Short-Form:</b>\n<a href=\"{sb['url']}\">{clean_sb_title}</a>\n↳ <i>{sb['views']:,} views ({sb['vph']} VPH) • {escape_html(sb['channel'])}</i>\n")
        else:
            msg_lines.append("")
            
    msg_lines.append("────────────────────────────")
    msg_lines.append("Kalo ada angle atau hook yang mau kita gas jadi script hari ini, colek gue yaa Tam! Semangat produksinya! 💪✨\n")
    msg_lines.append("<i>By Now, Be Nice! ✨</i>")
    
    report_text = "\n".join(msg_lines)
    
    # Phase 5: Delivery
    if bot_token and chat_id:
        print(f"\nMengirim laporan baru ke Telegram ({chat_id})...")
        sent = send_telegram_message(bot_token, chat_id, report_text)
        if sent:
            print("✅ SUKSES! Laporan ter-upgrade berhasil terkirim ke Telegram!")
        else:
            print("❌ GAGAL MENGIRIM KE TELEGRAM.")
    else:
        print("\n[Info] TELEGRAM_CHAT_ID belum diset di .env")

if __name__ == "__main__":
    run_pipeline()
