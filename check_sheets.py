import gspread
from google.oauth2.service_account import Credentials

# ===== Google Sheets setup =====
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Use google.oauth2.service_account.Credentials (modern method)
creds = Credentials.from_service_account_file(
    "my-telegram-bot-key.json", scopes=scope
)

# Authorize client
client = gspread.authorize(creds)

# ===== Open the spreadsheet =====
s = client.open("Telegram Dating Bot DB")  # make sure the name matches exactly

# ===== Access the 'Users' worksheet =====
sheet = s.worksheet("Users")

# ===== Test: Print all records in the sheet =====
print(sheet.get_all_records())
