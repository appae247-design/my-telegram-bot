# bot_server/main.py

from fastapi import FastAPI
from pydantic import BaseModel

# This is the "app" attribute the error message is looking for.
app = FastAPI()

class BotRequest(BaseModel):
    message: str
    user_id: str | None = None

class BotResponse(BaseModel):
    reply: str

@app.post("/ask-bot", response_model=BotResponse)
async def ask_bot(request: BotRequest):
    user_message = request.message
    bot_reply = ""

    # --- PASTE YOUR BOT LOGIC HERE ---
    # For now, we'll just echo the message back.
    bot_reply = f"You said: {user_message}"
    # --- END OF BOT LOGIC ---

    return {"reply": bot_reply}

@app.get("/")
def read_root():
    return {"message": "Bot server is running!"}