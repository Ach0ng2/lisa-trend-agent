import requests
import time
from typing import List, Dict

TARGET_SUBREDDITS = [
    "technology",
    "gadgets",
    "artificial",
    "LocalLLaMA",
    "android",
    "apple"
]

def fetch_reddit_posts(subreddit: str, limit: int = 15) -> List[Dict]:
    """
    Mengambil postingan terhangat dari subreddit via public JSON feed.
    100% gratis, tanpa API secret, menghitung upvote velocity per jam.
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TrendAgent/1.0"
    }
    posts = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            children = data.get("data", {}).get("children", [])
            current_time = time.time()
            
            for child in children:
                item = child.get("data", {})
                title = item.get("title", "")
                score = item.get("score", 0)
                num_comments = item.get("num_comments", 0)
                created_utc = item.get("created_utc", current_time)
                permalink = f"https://reddit.com{item.get('permalink', '')}"
                
                # Hitung usia postingan dalam jam
                age_hours = max((current_time - created_utc) / 3600.0, 0.5)
                # Upvote velocity: upvotes per hour
                velocity = round(score / age_hours, 1)
                
                posts.append({
                    "title": title,
                    "subreddit": subreddit,
                    "score": score,
                    "comments": num_comments,
                    "age_hours": round(age_hours, 1),
                    "velocity": velocity,
                    "url": permalink
                })
        else:
            print(f"[Reddit Error] r/{subreddit} returned status {response.status_code}")
    except Exception as e:
        print(f"[Reddit Exception] r/{subreddit}: {e}")
    return posts

def fetch_all_tech_reddit(min_velocity: float = 20.0) -> List[Dict]:
    """
    Mengambil postingan dari seluruh target subreddit dan memfilter hanya yang memiliki velocity tinggi.
    """
    all_hot_posts = []
    for sub in TARGET_SUBREDDITS:
        posts = fetch_reddit_posts(sub, limit=10)
        for p in posts:
            if p["velocity"] >= min_velocity:
                all_hot_posts.append(p)
        time.sleep(0.5) # Beri jeda kecil agar sopan
    
    # Sort berdasarkan velocity tertinggi
    all_hot_posts.sort(key=lambda x: x["velocity"], reverse=True)
    return all_hot_posts

if __name__ == "__main__":
    print("Testing Reddit Tech Listening...")
    hot_posts = fetch_all_tech_reddit(min_velocity=15.0)
    print(f"Ditemukan {len(hot_posts)} postingan dengan velocity tinggi:")
    for p in hot_posts[:5]:
        print(f" - [{p['subreddit']}] ({p['velocity']} upvotes/hr) {p['title'][:80]}...")
