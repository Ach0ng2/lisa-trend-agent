import requests
import datetime
import re
from typing import Dict, Any, Optional, List

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# Regex untuk mendeteksi aksara non-Latin
NON_LATIN_REGEX = re.compile(r'[\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F\u0400-\u04FF\u4E00-\u9FFF\uAC00-\uD7AF\u3040-\u30FF]')

GIMMICK_WORDS = [
    "1000°", "1000 degree", "hot metal ball", "molten", "hydraulic press",
    "blendtec", "will it blend", "hammer test", "crushed by", "lava",
    "microwave test", "drop from helicopter", "gun test", "bullet test"
]

STOP_WORDS = {
    'review', 'unboxing', 'vs', 'dan', 'and', 'the', 'in', 'on', 'for', 'with',
    'indonesia', 'terbaru', 'hp', 'gadget', 'test', 'hands', 'first', 'impressions',
    'cara', 'setting', 'harga', 'worth', 'it', 'gak', 'bocoran', 'resmi'
}

def clean_query_entity(query: str) -> str:
    words = query.strip().split()
    cleaned = [w for w in words if w.lower() not in STOP_WORDS]
    if cleaned:
        return " ".join(cleaned)
    return query

def extract_essential_tokens(query: str) -> List[str]:
    clean_q = clean_query_entity(query).lower()
    tokens = [w for w in re.findall(r'[a-zA-Z0-9]+', clean_q) if w not in STOP_WORDS]
    return tokens

def is_credible_tech_video(title: str) -> bool:
    if not title:
        return False
    if NON_LATIN_REGEX.search(title):
        return False
    lower_t = title.lower()
    for g in GIMMICK_WORDS:
        if g in lower_t:
            return False
    return True

def matches_query_tokens(tokens: List[str], text: str) -> bool:
    if not tokens:
        return True
    t_clean = text.lower().replace("-", " ").replace("_", " ")
    return all(tok in t_clean for tok in tokens)

def fetch_top_video_by_type(query: str, api_key: str, duration: str = "medium", days_back: int = 180) -> Optional[Dict[str, Any]]:
    """
    Super-fast batch search: mengambil 15 video sekaligus dalam 1 request batch video stats.
    Kecepatan: 15x lebih cepat dibanding query satu-satu!
    """
    clean_q = clean_query_entity(query)
    tokens = extract_essential_tokens(clean_q)
    now = datetime.datetime.now(datetime.timezone.utc)
    published_after = (now - datetime.timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    search_params = {
        "part": "snippet",
        "q": clean_q,
        "type": "video",
        "videoDuration": duration,
        "order": "viewCount",
        "publishedAfter": published_after,
        "maxResults": 15,
        "key": api_key
    }
    
    try:
        s_res = requests.get(YOUTUBE_SEARCH_URL, params=search_params, timeout=8)
        s_data = s_res.json()
        items = s_data.get("items", [])
        if not items:
            return None
            
        video_ids = [item["id"]["videoId"] for item in items if "id" in item and "videoId" in item["id"]]
        if not video_ids:
            return None
            
        # 1 SINGLE BATCH CALL UNTUK SEMUA VIDEO!
        v_res = requests.get(YOUTUBE_VIDEOS_URL, params={
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
            "key": api_key
        }, timeout=8)
        
        v_data = v_res.json()
        v_items = v_data.get("items", [])
        
        candidates = []
        for v in v_items:
            v_id = v.get("id")
            stats = v.get("statistics", {})
            snippet = v.get("snippet", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            
            if not is_credible_tech_video(title):
                continue
                
            in_title = matches_query_tokens(tokens, title)
            in_desc = matches_query_tokens(tokens, description)
            
            if tokens and not (in_title or in_desc):
                continue
                
            views = int(stats.get("viewCount", 0))
            if views < 500:
                continue
                
            pub_str = snippet.get("publishedAt", "")
            if pub_str:
                pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                age_hours = max((now - pub_dt).total_seconds() / 3600.0, 1.0)
            else:
                age_hours = 24.0
            vph = round(views / age_hours, 1)
            
            candidates.append({
                "title": title,
                "channel": snippet.get("channelTitle", ""),
                "views": views,
                "age_hours": round(age_hours, 1),
                "vph": vph,
                "in_title": in_title,
                "url": f"https://youtube.com/watch?v={v_id}"
            })
            
        if candidates:
            # Prioritas in_title dulu, baru views tertinggi
            candidates.sort(key=lambda x: (1 if x["in_title"] else 0, x["views"]), reverse=True)
            return candidates[0]
            
    except Exception as e:
        print(f"[Search Video Batch Error] '{clean_q}' ({duration}): {e}")
    return None

def evaluate_topic_supply_demand(topic: str, api_key: str) -> Dict[str, Any]:
    long_video = fetch_top_video_by_type(topic, api_key, duration="medium", days_back=180)
    short_video = fetch_top_video_by_type(topic, api_key, duration="short", days_back=180)
    
    if not long_video:
        long_video = fetch_top_video_by_type(topic, api_key, duration="medium", days_back=730)
    if not short_video:
        short_video = fetch_top_video_by_type(topic, api_key, duration="short", days_back=730)
        
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
    elif top_views > 1000:
        arbitrage_score = 6.2
        status = "Moderate Momentum"
    else:
        arbitrage_score = 4.5
        status = "Low Traffic / Emerging Niche"
        
    return {
        "topic": topic,
        "arbitrage_score": arbitrage_score,
        "status": status,
        "long_benchmark": long_video,
        "short_benchmark": short_video
    }

def escape_html(text: str) -> str:
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
