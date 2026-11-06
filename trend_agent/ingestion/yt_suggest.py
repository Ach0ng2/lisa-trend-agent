import requests
import json
import urllib.parse
from typing import List

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

def get_yt_suggestions(query: str, client: str = "firefox") -> List[str]:
    """
    Mengambil query autocomplete langsung dari endpoint publik YouTube suggest.
    100% gratis, tanpa token API, tanpa kuota.
    """
    params = {
        "client": client,
        "ds": "yt",
        "q": query
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(SUGGEST_URL, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Response format: [query, [suggestion1, suggestion2, ...]]
            if len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception as e:
        print(f"[YT Suggest Error] Query '{query}': {e}")
    return []

def harvest_wildcard_suggestions(entity: str) -> List[str]:
    """
    Melakukan wildcard crawling dengan pola pertanyaan dan komparasi penonton.
    """
    patterns = [
        f"{entity} vs",
        f"kenapa {entity}",
        f"cara {entity}",
        f"{entity} worth it",
        f"review {entity}",
        f"kekurangan {entity}"
    ]
    results = set()
    for pattern in patterns:
        suggestions = get_yt_suggestions(pattern)
        for s in suggestions:
            results.add(s)
    return sorted(list(results))

if __name__ == "__main__":
    test_entity = "S26 Ultra"
    print(f"Testing YT Suggest for: {test_entity}...")
    suggestions = harvest_wildcard_suggestions(test_entity)
    print(f"Ditemukan {len(suggestions)} pola pencarian:")
    for item in suggestions[:10]:
        print(f" - {item}")
