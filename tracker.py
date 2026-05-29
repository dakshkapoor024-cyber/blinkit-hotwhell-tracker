import requests
import time
import json
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────────────────────
BOT_TOKEN      = "8541447716:AAFxmfgWOZHakb2bn3dgTtveymTDP9yEfIM"
CHAT_ID        = "6375136265"
CHECK_INTERVAL = 45

TARGET_MODELS  = ["ferrari", "kick sauber", "sauber", "porsche 911", "porsche 911 carrera"]

# Mayur Vihar Phase 3
LATITUDE  = "28.6066"
LONGITUDE = "77.3130"

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
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

# ── BLINKIT SEARCH ─────────────────────────────────────────────────────────────
def check_blinkit():
    session = requests.Session()

    try:
        session.get(
            "https://blinkit.com",
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36"},
            timeout=10
        )
    except:
        pass

    url = "https://blinkit.com/v6/search/"
    headers = {
        "User-Agent":      "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept":          "application/json",
        "Accept-Language": "en-IN",
        "lat":             LATITUDE,
        "lon":             LONGITUDE,
        "Referer":         "https://blinkit.com/",
        "Origin":          "https://blinkit.com",
        "app_client":      "consumer",
        "web_app_version": "1000000",
    }
    params = {"q": "hot wheels", "start": 0, "size": 20}

    try:
        r = session.get(url, headers=headers, params=params, timeout=15)
        print(f"[{now()}] Status: {r.status_code}")

        if r.status_code != 200:
            return []

        data = r.json()
        products = []

        def dig(obj):
            if isinstance(obj, dict):
                name = obj.get("name", "")
                if name and is_target(name):
                    qty = obj.get("quantity", obj.get("inventory", {}).get("quantity", 1) if isinstance(obj.get("inventory"), dict) else 1)
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

# ── MAIN ──────────────────────────────────────────────────────────────────────
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
        f"🔄 Every {CHECK_INTERVAL}s\n\n"
        "Will ping you the moment stock appears 🚗"
    )

    alerted_ids = set()
    check_count = 0

    while True:
        try:
            check_count += 1
            products = check_blinkit()

            if products:
                new_stock = [p for p in products if p["in_stock"] and p["id"] not in alerted_ids]
                if new_stock:
                    lines = ["🚨 <b>HOTWHEELS IN STOCK ON BLINKIT!</b> 🚗\n"]
                    for p in new_stock:
                        lines.append(f"<b>{p['name']}</b>\n💰 ₹{p['price']} — ✅ In Stock\n👉 https://blinkit.com/s/?q=hot+wheels\n")
                    send_telegram("\n".join(lines))
                    for p in new_stock:
                        alerted_ids.add(p["id"])
                    print(f"[{now()}] ✅ ALERT SENT!")
                else:
                    print(f"[{now()}] Check #{check_count} — {len(products)} found, none in stock")
                alerted_ids &= {p["id"] for p in products if p["in_stock"]}
            else:
                print(f"[{now()}] Check #{check_count} — No results")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            send_telegram("🛑 Tracker stopped.")
            break
        except Exception as e:
            print(f"[{now()}] Loop error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
