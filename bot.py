import os
from dotenv import load_dotenv
# Load .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    exit("ERROR: BOT_TOKEN not found in environment.")

else:
    print("✅ BOT_TOKEN successfully loaded.")

# bot.py -- compatible with python-telegram-bot v13.x
import os
import logging
import random
from datetime import date
from typing import Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    Filters,
)

# Optional Google Sheets support (only used if gspread is available and creds present)
try:
    import gspread
    from google.oauth2.service_account import Credentials

    GS_SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Try to load credentials file if present
    if os.path.exists("my-telegram-bot-key.json"):
        gs_creds = Credentials.from_service_account_file("my-telegram-bot-key.json", scopes=GS_SCOPES)
        gs_client = gspread.authorize(gs_creds)
        # change this to your spreadsheet name and worksheet title
        try:
            gs_sheet = gs_client.open("Telegram Dating Bot DB").worksheet("Users")
            print("✅ Google Sheets connected:", gs_sheet.title)
        except Exception as e:
            gs_sheet = None
            print("⚠️ Google Sheets present but couldn't open sheet:", e)
    else:
        gs_client = None
        gs_sheet = None
except Exception:
    gs_client = None
    gs_sheet = None

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("ERROR: BOT_TOKEN not found in environment. Set BOT_TOKEN before running.")
    raise SystemExit(1)

# In-memory stores (fallback). You can store to Sheets or DB if you prefer.
user_state: Dict[int, str] = {}
user_data: Dict[int, Dict[str, Any]] = {}

# States
S_ASK_NAME = "ASK_NAME"
S_ASK_BIRTHDATE = "ASK_BIRTHDATE"
S_ASK_AGE_PREF = "ASK_AGE_PREF"
S_ASK_GENDER = "ASK_GENDER"
S_ASK_PREF = "ASK_PREF"
S_ASK_LOCATION = "ASK_LOCATION"
S_ASK_PHOTO = "ASK_PHOTO"
S_CONFIRM = "CONFIRM"
S_SHOW_MATCH = "SHOW_MATCH"
S_REQUIRE_VERIFICATION = "REQUIRE_VERIFICATION"
S_IDLE = "IDLE"

TRIGGER_KEYWORDS = {"hi", "hello", "start", "dating"}

# Example profiles (replace with actual source or spreadsheet)
PROFILES = [
    {"name": "Sarah", "age": 27, "bio": "Love music, travel, and deep conversations.", "location": "Lagos", "image": "https://picsum.photos/seed/sarah/400/400", "gender": "Female"},
    {"name": "Daniel", "age": 29, "bio": "Entrepreneur & foodie looking for a real connection.", "location": "Abuja", "image": "https://picsum.photos/seed/daniel/400/400", "gender": "Male"},
    {"name": "Funke", "age": 25, "bio": "Artist and nature lover.", "location": "Ibadan", "image": "https://picsum.photos/seed/funke/400/400", "gender": "Female"},
]

PHOTO_DIR = "user_photos"
VIDEO_DIR = "user_videos"
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


def init_user(uid: int):
    user_state[uid] = S_ASK_NAME
    user_data[uid] = {
        "seen_matches": set(),
        "matches_shown_count": 0,
        "verified": False,
    }


def save_to_sheets(uid: int):
    """Optional: write brief user summary to Google Sheets if available."""
    if not gs_sheet:
        return
    data = user_data.get(uid, {})
    try:
        # Append a row (timestamp, user_id, name, age, gender, preference, location, verified)
        row = [
            str(date.today()),
            str(uid),
            data.get("first_name", ""),
            str(data.get("age", "")),
            data.get("gender", ""),
            data.get("preference", ""),
            data.get("location", ""),
            "yes" if data.get("verified") else "no",
        ]
        gs_sheet.append_row(row)
        print(f"[Sheets] saved user {uid}")
    except Exception as exc:
        print("⚠️ Failed saving to sheets:", exc)


def get_match_for_pref(preference: str, exclude_idx: set):
    candidates = []
    for i, p in enumerate(PROFILES):
        if i in exclude_idx:
            continue
        if preference == "Anyone":
            candidates.append((p, i))
        elif preference == "Men" and p["gender"].lower().startswith("m"):
            candidates.append((p, i))
        elif preference == "Women" and p["gender"].lower().startswith("f"):
            candidates.append((p, i))
    if not candidates:
        return None, None
    return random.choice(candidates)


def send_typing(bot, chat_id, seconds=1.0):
    try:
        bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass


# --- Handlers ---
def start_cmd(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    init_user(uid)
    send_typing(context.bot, update.effective_chat.id)
    update.message.reply_text("Hi 👋 Welcome to AE Social & Lifestyle Dating!\nWhat's your first name?")


def text_handler(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    text = update.message.text.strip() if update.message and update.message.text else ""
    if not text:
        return

    norm = text.lower().lstrip("/") if text.startswith("/") else text.lower()

    # Start/restart if unknown or trigger
    if uid not in user_state or norm in TRIGGER_KEYWORDS:
        init_user(uid)
        send_typing(context.bot, update.effective_chat.id)
        update.message.reply_text("Hi 👋 Welcome! What's your first name?")
        return

    state = user_state.get(uid, S_IDLE)

    if state == S_ASK_NAME:
        user_data[uid]["first_name"] = text
        user_state[uid] = S_ASK_BIRTHDATE
        send_typing(context.bot, update.effective_chat.id)
        update.message.reply_text("Great! What is your date of birth? (YYYY-MM-DD)")
        return

    if state == S_ASK_BIRTHDATE:
        try:
            birthdate = date.fromisoformat(text)
            today = date.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            if age < 18:
                update.message.reply_text("Sorry — you must be 18+ to use this service.")
                init_user(uid)
                return
            user_data[uid]["birthdate"] = text
            user_data[uid]["age"] = age
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("18-25", callback_data="age_pref|18-25"),
                 InlineKeyboardButton("26-35", callback_data="age_pref|26-35")],
                [InlineKeyboardButton("36-50", callback_data="age_pref|36-50"),
                 InlineKeyboardButton("51+", callback_data="age_pref|51-99")]
            ])
            user_state[uid] = S_ASK_AGE_PREF
            send_typing(context.bot, update.effective_chat.id)
            update.message.reply_text("What age range do you prefer for matches?", reply_markup=kb)
        except ValueError:
            update.message.reply_text("Invalid date format. Use YYYY-MM-DD.")
        return

    if state == S_ASK_LOCATION:
        user_data[uid]["location"] = text
        # ask for photo after location
        user_state[uid] = S_ASK_PHOTO
        update.message.reply_text("Please upload a real photo of yourself (a clear face/fullbody photo). 📸")
        return

    # default fallback
    update.message.reply_text("Please use the shown buttons, or type 'hi' to restart.")


def handle_photo(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    state = user_state.get(uid)
    if state != S_ASK_PHOTO:
        update.message.reply_text("I wasn't expecting a photo right now. If you'd like to start, type 'hi'.")
        return

    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    path = os.path.join(PHOTO_DIR, f"{uid}.jpg")
    try:
        file.download(path)
    except Exception as e:
        print("⚠️ Failed to download photo:", e)
        update.message.reply_text("Could not save your photo — please try again.")
        return

    user_data[uid]["photo_path"] = path
    update.message.reply_text("Photo received ✅. Here's what I have so far:")
    # send summary + confirm buttons
    fn = user_data[uid].get("first_name", "—")
    age = user_data[uid].get("age", "—")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Yes ✅", callback_data="confirm|yes"),
                                InlineKeyboardButton("No ❌", callback_data="confirm|no")]])
    update.message.reply_text(f"Name: {fn}\nAge: {age}\nLocation: {user_data[uid].get('location','—')}\nIs this correct?", reply_markup=kb)
    user_state[uid] = S_CONFIRM


def handle_video(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    state = user_state.get(uid)
    if state != S_REQUIRE_VERIFICATION:
        update.message.reply_text("I'm not expecting a verification video right now.")
        return

    # Accept regular video or video note
    video = update.message.video or update.message.video_note
    if not video:
        update.message.reply_text("Please send a video file (not a photo).")
        return

    file = context.bot.get_file(video.file_id)
    path = os.path.join(VIDEO_DIR, f"{uid}.mp4")
    try:
        file.download(path)
    except Exception as e:
        print("⚠️ Failed to download video:", e)
        update.message.reply_text("Could not save your video — please try again.")
        return

    user_data[uid]["verification_video"] = path
    user_data[uid]["verified"] = True
    user_state[uid] = S_SHOW_MATCH
    update.message.reply_text("Thank you — your verification video is received. ✅ You are now verified.")
    # optionally record to sheet
    save_to_sheets(uid)


def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    uid = user.id
    data = query.data or ""
    parts = data.split("|")
    action = parts[0]
    state = user_state.get(uid)

    # always answer callback to remove loading state
    query.answer()

    if not state:
        init_user(uid)
        try:
            query.edit_message_text("Restarting. What's your first name?")
        except Exception:
            query.message.reply_text("Restarting. What's your first name?")
        return

    if action == "age_pref" and state == S_ASK_AGE_PREF:
        min_age, max_age = parts[1].split("-")
        user_data[uid]["age_preference_min"] = int(min_age)
        user_data[uid]["age_preference_max"] = int(max_age)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Male 👨", callback_data="gender|Male"),
                                    InlineKeyboardButton("Female 👩", callback_data="gender|Female"),
                                    InlineKeyboardButton("Other 🌈", callback_data="gender|Other")]])
        try:
            query.edit_message_text("What’s your gender?", reply_markup=kb)
        except Exception:
            query.message.reply_text("What’s your gender?", reply_markup=kb)
        user_state[uid] = S_ASK_GENDER
        return

    if action == "gender" and state == S_ASK_GENDER:
        user_data[uid]["gender"] = parts[1]
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Men 👨", callback_data="pref|Men"),
                                    InlineKeyboardButton("Women 👩", callback_data="pref|Women"),
                                    InlineKeyboardButton("Anyone 💫", callback_data="pref|Anyone")]])
        try:
            query.edit_message_text("Who would you like to meet?", reply_markup=kb)
        except Exception:
            query.message.reply_text("Who would you like to meet?", reply_markup=kb)
        user_state[uid] = S_ASK_PREF
        return

    if action == "pref" and state == S_ASK_PREF:
        user_data[uid]["preference"] = parts[1]
        # ask location next
        try:
            query.edit_message_text("Please share your location (send it by tapping the paperclip -> Location) to find nearby matches 📍")
        except Exception:
            query.message.reply_text("Please share your location (send it by tapping the paperclip -> Location) to find nearby matches 📍")
        user_state[uid] = S_ASK_LOCATION
        return

    if action == "confirm" and state == S_CONFIRM:
        if parts[1] == "yes":
            # save to sheet (optional) and move to matching
            save_to_sheets(uid)
            user_state[uid] = S_SHOW_MATCH
            user_data[uid].setdefault("seen_matches", set())
            user_data[uid]["matches_shown_count"] = 0
            try:
                query.edit_message_text("Perfect! Let’s find someone for you 💞")
            except Exception:
                query.message.reply_text("Perfect! Let’s find someone for you 💞")
            # show first match
            show_match(uid, context)
        else:
            init_user(uid)
            try:
                query.edit_message_text("No problem — let's start again. What's your first name?")
            except Exception:
                query.message.reply_text("No problem — let's start again. What's your first name?")
        return

    if action == "match" and state == S_SHOW_MATCH:
        # parts[1] should be 'interested' or 'next'
        if len(parts) < 2:
            query.answer("Unknown action.")
            return

        sub = parts[1]
        if sub == "interested":
            # If the original message was a photo (match card), edit its caption; else edit text.
            try:
                if query.message.photo or query.message.caption:
                    # edit caption if photo exists
                    query.message.edit_caption("Awesome! We'll let them know you're interested. 💌 Searching for the next match...")
                else:
                    query.edit_message_text("Awesome! We'll let them know you're interested. 💌 Searching for the next match...")
            except Exception as e:
                # fallback: send a new message
                logger.warning("Could not edit match message: %s", e)
                try:
                    query.message.reply_text("Awesome! We'll let them know you're interested. 💌 Searching for the next match...")
                except Exception:
                    pass
            # then show next match
            show_match(uid, context)
            return

        if sub == "next":
            # try to delete previous match message if possible, but continue
            try:
                query.delete_message()
            except Exception:
                pass
            show_match(uid, context)
            return

    # default help if unknown
    try:
        query.message.reply_text("Please follow the current prompt or type 'hi' to restart.")
    except Exception:
        pass


def show_match(uid: int, context: CallbackContext):
    """Send a match card (photo + caption) with only Interested and Next buttons.

    Also increase the matches_shown_count and trigger verification after 3 matches.
    """
    if uid not in user_data:
        init_user(uid)
    pref = user_data[uid].get("preference", "Anyone")
    seen = set(user_data[uid].get("seen_matches", set()))
    profile, idx = get_match_for_pref(pref, seen)
    if profile is None:
        context.bot.send_message(chat_id=uid, text="No matches right now for your preferences. Try again later or change preferences.")
        user_state[uid] = S_IDLE
        return

    # Mark seen
    seen.add(idx)
    user_data[uid]["seen_matches"] = seen
    user_data[uid]["last_match_idx"] = idx
    user_data[uid]["matches_shown_count"] = user_data[uid].get("matches_shown_count", 0) + 1

    caption = f"Meet {profile['name']}, {profile['age']} 🌸\n📍 {profile['location']}\n💬 {profile['bio']}"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("❤️ Interested", callback_data="match|interested"),
         InlineKeyboardButton("⏭️ Next", callback_data="match|next")]
    ])
    # send photo with caption and buttons
    try:
        context.bot.send_photo(chat_id=uid, photo=profile["image"], caption=caption, reply_markup=kb)
    except Exception as e:
        # fallback to plain message if photo sending fails
        logger.warning("Failed to send photo, sending text: %s", e)
        context.bot.send_message(chat_id=uid, text=caption, reply_markup=kb)

    # After showing 3 matches, require video verification
    if user_data[uid]["matches_shown_count"] >= 3 and not user_data[uid].get("verified", False):
        # set a state that expects a verification video next
        user_state[uid] = S_REQUIRE_VERIFICATION
        # ask the user to record a short video mimicking a posture call-to-action
        context.bot.send_message(
            chat_id=uid,
            text=(
                "To keep AE Social safe, please record a short verification video now.\n\n"
                "Action: Stand and raise your right hand above your head for 2-3 seconds, like the example posture.\n"
                "Record a short video (5-10s) and send it here. This confirms the account is real."
            )
        )
    else:
        user_state[uid] = S_SHOW_MATCH


def location_handler(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    if user_state.get(uid) == S_ASK_LOCATION:
        loc = update.message.location
        loc_text = f"{loc.latitude:.5f}, {loc.longitude:.5f}"
        user_data[uid]["location"] = loc_text
        update.message.reply_text("Thanks! Location saved ✅ Please upload a real photo of yourself now.")
        user_state[uid] = S_ASK_PHOTO
    else:
        update.message.reply_text("I wasn't expecting a location right now. If you'd like to restart, type 'hi'.")


def error_handler(update: Update, context: CallbackContext):
    logger.exception("Update caused error: %s", context.error)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(["start", "help"], start_cmd))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), text_handler))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.video | Filters.video_note, handle_video))
    dp.add_handler(MessageHandler(Filters.location, location_handler))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_error_handler(error_handler)

    print("🤖 Bot is starting...")
    updater.start_polling()
    print("🤖 Bot is running...")
    updater.idle()


if __name__ == "__main__":
    main()
from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running fine on Render!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=main).start()  # your main() should start the Telegram bot
    run_flask()
