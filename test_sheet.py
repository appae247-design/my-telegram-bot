import gspread
from google.oauth2.service_account import Credentials

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("my-telegram-bot-key.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("Telegram Dating Bot DB").worksheet("Users")

print("✅ Connection successful:", sheet.title)
