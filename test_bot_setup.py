import gspread
from google.oauth2.service_account import Credentials
import os
import requests

# === CONFIGURE GOOGLE SHEETS ===
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "my-telegram-bot-key.json"

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("Telegram Dating Bot DB").worksheet("Users")
    print("✅ Google Sheets connection successful! Sheet title:", sheet.title)
except Exception as e:
    print("❌ Google Sheets connection failed!")
    print("Error:", e)

# === TEST TELEGRAM BOT TOKEN ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN is not set in environment variables.")
else:
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        resp = requests.get(url)
        data = resp.json()
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ Telegram bot is reachable! Bot username: @{bot_info.get('username')}")
        else:
            print("❌ Telegram bot token invalid or bot unreachable!")
            print("Response:", data)
    except Exception as e:
        print("❌ Error testing Telegram bot token:", e)
