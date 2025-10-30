# Telegram Dating Bot (AE Social & Lifestyle)

A small Telegram bot prototype that collects basic profile info and shows example matches.

## Requirements
- Python 3.10+ (tested with Python 3.14)
- A Telegram bot token from @BotFather

## Install

Create a virtual environment (recommended) and install dependencies:

```powershell
py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
```

## Configure
Set your bot token as an environment variable instead of editing the source:

```powershell
$env:BOT_TOKEN = "<your-token-here>"
```

Or replace the `TOKEN` variable in `bot.py` (not recommended for production).

Important: never commit your secrets (BOT_TOKEN, AIRTABLE_API_KEY, etc.) to
git. Use environment variables, a secret manager, or an untracked `.env` file
for local development.

### Airtable setup (optional)
If you want to use Airtable as the backend for storing confirmed profiles, set these environment variables with values from your Airtable account:

```powershell
$env:AIRTABLE_API_KEY = "key...."
$env:AIRTABLE_BASE_ID = "app...."
$env:AIRTABLE_TABLE_NAME = "Profiles"  # optional, defaults to 'Profiles'
```

The bot will attempt to save a user's confirmed profile to Airtable when these variables are set. If they are not present the bot will continue to work using the in-memory store.

## Run

```powershell
py -3 .\bot.py
```

The bot will start in polling mode and print `🤖 Bot is running...` when ready.

## Notes & Next steps
- Replace in-memory dictionaries with a persistent DB for production (SQLite/Redis/Postgres).
- Add validation and better error handling for inputs.
- Move `TOKEN` to a secure secrets manager or environment variable for deployment.
- Consider adding logging and tests.

## License
MIT
