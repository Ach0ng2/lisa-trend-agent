import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

GOOGLE_TRENDS_RSS_ID = "https://trends.google.com/trending/rss?geo=ID"
GOOGLE_TRENDS_RSS_US = "https://trends.google.com/trending/rss?geo=US"

def fetch_google_trends_rss(geo: str = "ID") -> List[Dict[str, str]]:
    """
    Mengambil trending topics harian dari Google Trends RSS.
    100% gratis, tanpa autentikasi, anti-blokir.
    """
    url = GOOGLE_TRENDS_RSS_ID if geo.upper() == "ID" else GOOGLE_TRENDS_RSS_US
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    trends = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Namespace ht biasanya digunakan Google Trends: https://trends.google.com/trending/rss
            namespaces = {'ht': 'https://trends.google.com/trending/rss'}
            
            for item in root.findall('./channel/item'):
                title = item.find('title').text if item.find('title') is not None else ""
                approx_traffic = item.find('ht:approx_traffic', namespaces)
                traffic_text = approx_traffic.text if approx_traffic is not None else "N/A"
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                description = item.find('description').text if item.find('description') is not None else ""
                
                if title:
                    trends.append({
                        "title": title.strip(),
                        "traffic": traffic_text.strip(),
                        "pub_date": pub_date.strip(),
                        "geo": geo.upper()
                    })
    except Exception as e:
        print(f"[Google Trends RSS Error] Geo '{geo}': {e}")
    return trends

if __name__ == "__main__":
    print("Testing Google Trends RSS (Indonesia)...")
    id_trends = fetch_google_trends_rss("ID")
    print(f"Berhasil menarik {len(id_trends)} trending topics di Indonesia:")
    for t in id_trends[:5]:
        print(f" - [{t['traffic']}] {t['title']}")
