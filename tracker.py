import requests
import time
import re
from datetime import datetime

BOT_TOKEN      = "8541447716:AAFxmfgW0ZHakb2bn3dgTtveymTDP9yEfIM"
CHAT_ID        = "6375136265"
CHECK_INTERVAL = 45

TARGET_MODELS  = ["ferrari", "kick sauber", "sauber", "porsche 911", "porsche 911 carrera"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[Telegram error] {e}")
        return False

def now():
    return datetime.now().strftime("%H:%M:%S")

def is_target(name):
    n = name.lower()
    return any(kw in n for kw in ["hot wheels", "hotwheels"]) and any(kw in n for kw in TARGET_MODELS)

def check_blinkit():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    try:
        r = requests.get(
            "https://blinkit.com/s/?q=hot+wheels",
            headers=headers,
            timeout=20
        )
        print(f"[{now()}] Status: {r.status_code} Size: {len(r.text)}")

        if r.status_code != 200:
            return []

        products = []
        matches = re.findall(r'"name"\s*:\s*"([^"]*)"', r.text, re.IGNORECASE)

        for name in matches:
            if is_target(name):
                products.append({
                    "name": name,
                    "price": "179",
                    "in_stock": True,
                    "id": name[:40],
                })

        return products

    except Exception as e:
        print(f"[{now()}] Error: {e}")
        return []

def main():
    print("=" * 50)
    print("  Blinkit Hotwheels Tracker")
    print("  Mayur Vihar Phase 3, Delhi")
    print(f"  Every {CHECK_INTERVAL}s")
    print("=" * 50)

    send_telegram(
        "🤖 <b>Hotwheels Tracker Started!</b>\n\n"
        "👀 Watching for:\n"
        "• Ferrari Die Cast\n"
        "• Kick Sauber F1 Die Cast\n"
        "• Porsche 911 Carrera Die Cast\n\n"
        "📍 Mayur Vihar Phase 3, Delhi\n"
        "⏱ Checking every 45 seconds"
    )

    seen = set()
    check_num = 0

    while True:
        check_num += 1
        products = check_blinkit()

        if products:
            for p in products:
                if p["id"] not in seen and p["in_stock"]:
                    seen.add(p["id"])
                    send_telegram(
                        f"🚨 <b>HOTWHEELS IN STOCK!</b>\n\n"
                        f"🚗 {p['name']}\n"
                        f"💰 ₹{p['price']}\n"
                        f"🛒 https://blinkit.com/s/?q=hot+wheels"
                    )
                    print(f"[{now()}] FOUND: {p['name']}")
        else:
            print(f"[{now()}] Check #{check_num} — No results")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
