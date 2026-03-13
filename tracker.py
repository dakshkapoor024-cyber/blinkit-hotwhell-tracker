import requests
import time

BOT_TOKEN = "8364216798:AAHOzY2cKv-1_mI4Kaz4JRV9Pes4fVm8Srs"
CHAT_ID = "6375136265"

API_URL = "https://blinkit.com/v1/layout/listing_widgets"

KEYWORD = "hot wheels"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "accept": "application/json"
    }

    params = {
        "page_index": "1",
        "q": "hot wheels"
    }

    r = requests.get(API_URL, headers=headers, params=params)

    if r.status_code != 200:
        return False

    data = r.text.lower()

    if KEYWORD in data:
        return True

    return False

print("Tracker started...")

while True:
    try:
        if check_stock():
            send_telegram("🔥 HOT WHEELS DETECTED ON BLINKIT!")
            print("Stock detected")
            time.sleep(60)
        else:
            print("Checking...")

    except Exception as e:
        print("Error:", e)

    time.sleep(2)