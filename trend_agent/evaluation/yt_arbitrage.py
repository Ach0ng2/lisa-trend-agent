import requests
import datetime
from typing import Dict, Any, Optional

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def get_best_video_stats(video_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Mengambil statistik detail video (views, likes) dan menghitung VPH.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key
    }
    try:
        res = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=10)
        data = res.json()
        items = data.get("items", [])
        if items:
            v = items[0]
            stats = v.get("statistics", {})
            snippet = v.get("snippet", {})
            views = int(stats.get("viewCount", 0))
            pub_str = snippet.get("publishedAt", "")
            if pub_str:
                pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                age_hours = max((now - pub_dt).total_seconds() / 3600.0, 1.0)
            else:
                age_hours = 24.0
            vph = round(views / age_hours, 1)
            return {
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "views": views,
                "age_hours": round(age_hours, 1),
                "vph": vph,
                "url": f"https://youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        print(f"[Video Stats Error] {e}")
    return None

def fetch_top_video_by_type(query: str, api_key: str, duration: str = "medium", days_back: int = 30) -> Optional[Dict[str, Any]]:
    """
    Mencari video terbaik dengan views terbanyak dalam rentang hari terakhir.
    duration: 'medium' (4-20 min / Long-Form) atau 'short' (<4 min / Shorts).
    """
    published_after = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoDuration": duration,
        "order": "viewCount",
        "publishedAfter": published_after,
        "maxResults": 3,
        "key": api_key
    }
    
    try:
        s_res = requests.get(YOUTUBE_SEARCH_URL, params=search_params, timeout=10)
        s_data = s_res.json()
        items = s_data.get("items", [])
        for item in items:
            v_id = item.get("id", {}).get("videoId")
            if v_id:
                stats = get_best_video_stats(v_id, api_key)
                # Filter: hanya ambil yang views-nya masuk akal (>1.000 views)
                if stats and stats["views"] >= 1000:
                    return stats
    except Exception as e:
        print(f"[Search Video Error] '{query}' ({duration}): {e}")
    return None

def evaluate_topic_supply_demand(topic: str, api_key: str) -> Dict[str, Any]:
    """
    Menghitung Arbitrage dan mengambil 2 benchmark kredibel:
    1. Long-Form Benchmark (Channel berbobot, views puluhan ribu / jutaan)
    2. Short-Form Viral Benchmark (Shorts meledak)
    """
    long_video = fetch_top_video_by_type(topic, api_key, duration="medium", days_back=30)
    short_video = fetch_top_video_by_type(topic, api_key, duration="short", days_back=30)
    
    # Hitung Arbitrage Score berdasarkan total traffic benchmark
    top_views = max(long_video["views"] if long_video else 0, short_video["views"] if short_video else 0)
    
    if top_views > 500000:
        arbitrage_score = 9.4
        status = "Mega Trend (Audiens Lapar & Valid)"
    elif top_views > 100000:
        arbitrage_score = 8.5
        status = "High Demand (Sangat Potensial)"
    elif top_views > 20000:
        arbitrage_score = 7.2
        status = "Healthy Growth (Niche Hangat)"
    else:
        arbitrage_score = 5.8
        status = "Moderate Momentum"
        
    return {
        "topic": topic,
        "arbitrage_score": arbitrage_score,
        "status": status,
        "long_benchmark": long_video,
        "short_benchmark": short_video
    }

if __name__ == "__main__":
    import os
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from dotenv import load_dotenv
    load_dotenv()
    
    key = os.getenv("YOUTUBE_API_KEY")
    if key:
        print("Testing Kredibel Benchmark on 'S26 Ultra'...")
        res = evaluate_topic_supply_demand("S26 Ultra", key)
        print("Status:", res["status"])
        print("Score:", res["arbitrage_score"])
        if res["long_benchmark"]:
            lb = res["long_benchmark"]
            print(f"Long-Form: {lb['title']} | Channel: {lb['channel']} | Views: {lb['views']:,} ({lb['vph']} VPH)")
        if res["short_benchmark"]:
            sb = res["short_benchmark"]
            print(f"Short-Form: {sb['title']} | Channel: {sb['channel']} | Views: {sb['views']:,} ({sb['vph']} VPH)")
