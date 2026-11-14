# -*- coding: utf-8 -*-
"""run_daily.py - تشغيل صيد + تقرير يومي مرة واحدة (يُستخدم من GitHub Actions أو cron)."""
import asyncio
import logging

from telegram import Bot

from config import require_token
from database import init_db
from hunter import execute_deep_hunt
from bot import send_digest_and_reminders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    init_db()
    execute_deep_hunt()
    async with Bot(token=require_token()) as bot:
        await send_digest_and_reminders(bot)


if __name__ == "__main__":
    asyncio.run(main())
