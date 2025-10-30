import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== Google Sheets setup =====
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Replace the filename below with the exact name of your JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "my-telegram-bot-key.json", scope
)

client = gspread.authorize(creds)

# ===== Open the spreadsheet =====
s = client.open("Telegram Dating Bot DB")

# ===== Access the 'Users' worksheet =====
sheet = s.worksheet("Users")

# ===== Test: Print all records in the sheet =====
print(sheet.get_all_records())
