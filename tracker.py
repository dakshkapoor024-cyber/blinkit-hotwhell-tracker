import requests
import time
from datetime import datetime

BOT_TOKEN      = "8541447716:AAFxmfgW0ZHakb2bn3dgTtveymTDP9yEfIM"
CHAT_ID        = "6375136265"
CHECK_INTERVAL = 45

TARGET_MODELS  = ["ferrari", "kick sauber", "sauber", "porsche 911", "porsche 911 carrera"]

LATITUDE  = "28.6066"
LONGITUDE = "77.3130"

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
    api_key = "29187163bf62494aa55fe404008383fcef5fce87a84"
    target_url = f"https://blinkit.com/v6/search/?q=hot+wheels&start=0&size=20"
    
    scrape_url = f"https://api.scrape.do?token={api_key}&url={target_url}&customHeaders=true"
    
    headers = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "app_client": "consumer",
        "web_app_version": "1000000",
    }

    try:
        r = requests.get(scrape_url, headers=headers, timeout=30)
        print(f"[{now()}] Status: {r.status_code}")

        if r.status_code != 200:
            return []

        data = r.json()
        products = []

        def dig(obj):
            if isinstance(obj, dict):
                name = obj.get("name", "")
                if name and is_target(name):
                    qty = obj.get("quantity", 1)
                    in_stock = int(qty) > 0 if str(qty).isdigit() else True
                    products.append({
                        "name": name,
                        "price": obj.get("price", obj.get("mrp", "N/A")),
                        "in_stock": in_stock,
                        "id": str(obj.get("id", name))[:40],
                    })
                for v in obj.values():
                    dig(v)
            elif isinstance(obj, list):
                for item in obj:
                    dig(item)

        dig(data)
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
