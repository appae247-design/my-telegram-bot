"""Simple entrypoint for starting the bot.

This file delegates to `bot.main()` so you can run `python main.py` or
use it as a process entrypoint in deployments.
"""
import platform

if platform.system() == "Windows":
    try:
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import bot

if __name__ == "__main__":
    bot.main()
