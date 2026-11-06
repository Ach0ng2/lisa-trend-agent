import requests
import datetime
from typing import Dict, List, Any

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def evaluate_topic_supply_demand(topic: str, api_key: str) -> Dict[str, Any]:
    """
    Menghitung supply vs demand arbitrage dan Views Per Hour (VPH) video YouTube terbaru.
    Biaya kuota: 100 unit (search) + 1 unit (video stats) = 101 unit per topik.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # 1. Search recent videos for topic
    search_params = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "order": "date",
        "maxResults": 10,
        "key": api_key
    }
    
    try:
        s_res = requests.get(YOUTUBE_SEARCH_URL, params=search_params, timeout=10)
        s_data = s_res.json()
        items = s_data.get("items", [])
        
        if not items:
            return {
                "topic": topic,
                "supply_recent_videos": 0,
                "avg_vph": 0.0,
                "arbitrage_score": 5.0,
                "status": "No Recent Videos (Fresh Territory)",
                "top_recent_videos": []
            }
        
        video_ids = [item["id"]["videoId"] for item in items if "id" in item and "videoId" in item["id"]]
        
        # 2. Get video statistics (views, likes)
        stats_params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": api_key
        }
        v_res = requests.get(YOUTUBE_VIDEOS_URL, params=stats_params, timeout=10)
        v_data = v_res.json()
        video_items = v_data.get("items", [])
        
        analyzed_videos = []
        total_vph = 0.0
        
        for v in video_items:
            v_id = v.get("id")
            stats = v.get("statistics", {})
            snippet = v.get("snippet", {})
            
            views = int(stats.get("viewCount", 0))
            pub_str = snippet.get("publishedAt", "")
            channel_title = snippet.get("channelTitle", "")
            title = snippet.get("title", "")
            
            if pub_str:
                pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                age_hours = max((now - pub_dt).total_seconds() / 3600.0, 0.5)
            else:
                age_hours = 24.0
                
            vph = round(views / age_hours, 1)
            total_vph += vph
            
            analyzed_videos.append({
                "title": title,
                "channel": channel_title,
                "views": views,
                "age_hours": round(age_hours, 1),
                "vph": vph,
                "url": f"https://youtube.com/watch?v={v_id}"
            })
            
        count = len(analyzed_videos)
        avg_vph = round(total_vph / count, 1) if count > 0 else 0.0
        
        # Arbitrage Calculation:
        # Jika VPH tinggi (>300 VPH) dan video di bawah 7 hari masih sedikit, score tinggi.
        # Score skala 1.0 - 10.0
        if avg_vph > 500:
            arbitrage_score = 9.2
            status = "High Demand Wave (Viral / Breaking)"
        elif avg_vph > 150:
            arbitrage_score = 7.8
            status = "Healthy Growth (High Opportunity)"
        elif avg_vph > 50:
            arbitrage_score = 6.2
            status = "Moderate Momentum"
        else:
            arbitrage_score = 4.5
            status = "Low Velocity / Saturated"
            
        return {
            "topic": topic,
            "supply_recent_videos": count,
            "avg_vph": avg_vph,
            "arbitrage_score": arbitrage_score,
            "status": status,
            "top_recent_videos": analyzed_videos[:3]
        }
        
    except Exception as e:
        print(f"[YT Arbitrage Error] '{topic}': {e}")
        return {
            "topic": topic,
            "supply_recent_videos": 0,
            "avg_vph": 0.0,
            "arbitrage_score": 5.0,
            "status": f"Error: {e}",
            "top_recent_videos": []
        }

if __name__ == "__main__":
    import os
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv("YOUTUBE_API_KEY")
    if key:
        print("Testing YouTube Arbitrage Engine on 'S26 Ultra'...")
        result = evaluate_topic_supply_demand("S26 Ultra", key)
        print(f"Status: {result['status']}")
        print(f"Avg VPH: {result['avg_vph']}")
        print(f"Arbitrage Score: {result['arbitrage_score']}/10")
        print("Recent Top Videos:")
        for v in result["top_recent_videos"]:
            print(f" - [{v['vph']} VPH] {v['title'][:60]} ({v['channel']})")
    else:
        print("YOUTUBE_API_KEY belum ada.")
