import requests
from typing import Optional

def send_telegram_message(token: str, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """
    Mengirim pesan ke pengguna Telegram via Bot API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data.get("ok"):
            return True
        else:
            print(f"[Telegram Error] {data.get('description')}")
            return False
    except Exception as e:
        print(f"[Telegram Exception] {e}")
        return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if token and chat_id:
        print(f"Testing Telegram message to {chat_id}...")
        success = send_telegram_message(token, chat_id, "<b>Halo Tam!</b>\nIni tes pesan dari Lisa Trend Intelligence Agent.")
        print("Status kirim:", success)
    else:
        print("Token atau Chat ID belum diset di .env")
