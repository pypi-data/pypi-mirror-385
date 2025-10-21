
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/spammer/spammer_commands.py
#
# دستورات اسپمر (time/kill/stop_kill/start_spammer/stop_spammer)
# و تایمر برنامه‌ریز اسپمر (start_timer/stop_timer/timer_status + تنظیمات)
#
# استفاده در main.py:
#   from SBself.moudels.spammer.spammer_commands import register as register_spammer_commands
#   register_spammer_commands(app)

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter

from .spammer_manager import (
    start_spammer,
    stop_spammer,
    set_spam_time,
    start_spam_on_message,
    stop_spam_on_message,
)
from .spammer_via_schedule import (
    start_scheduler_spammer,
    stop_scheduler_spammer,
    get_timer_status,
    set_timer_text,
    set_timer_interval,
    set_timer_repeat,
)
from .auto_timer_handler import handle_auto_timer

def register(app: Client) -> None:
    # =============================
    # 🔥 SPAMMER
    # =============================
    @app.on_message(admin_filter & filters.command("time", prefixes=["/", ""]))
    async def _time(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("time <seconds>")
        try:
            await m.reply(await set_spam_time(int(m.command[1])))
        except Exception:
            await m.reply("مقدار زمان نامعتبر است.")

    @app.on_message(admin_filter & filters.command("kill", prefixes=["/", ""]) & filters.reply)
    async def _kill(client: Client, m: Message):
        # شروع اسپم روی پیام ریپلای‌شده
        await start_spam_on_message(client, m.chat.id, m.reply_to_message.id)
        # پیام موفقیت جداگانه لازم نیست؛ تابع بیزنس‌لاجیک جریان را مدیریت می‌کند.

    @app.on_message(admin_filter & filters.command("stop_kill", prefixes=["/", ""]))
    async def _stop_kill(client: Client, m: Message):
        await stop_spam_on_message()
        await m.reply("🛑 حالت kill متوقف شد.")

    @app.on_message(admin_filter & filters.command("start_spammer", prefixes=["/", ""]))
    async def _start_spam(client: Client, m: Message):
        # در نسخهٔ شما فقط چت فعلی را استارت می‌زنیم؛
        # اگر چند چت می‌خواهی، آرایهٔ chat_ids را گسترش بده.
        await m.reply(await start_spammer(client, [m.chat.id]))

    @app.on_message(admin_filter & filters.command("stop_spammer", prefixes=["/", ""]))
    async def _stop_spam(client: Client, m: Message):
        await m.reply(await stop_spammer())

    # =============================
    # ⏱ TIMER (SCHEDULE SPAMMER)
    # =============================
    @app.on_message(admin_filter & filters.command("start_timer", prefixes=["/", ""]))
    async def _timer_start(client: Client, m: Message):
        await m.reply(await start_scheduler_spammer(client, m.chat.id))

    @app.on_message(admin_filter & filters.command("stop_timer", prefixes=["/", ""]))
    async def _timer_stop(client: Client, m: Message):
        await m.reply(await stop_scheduler_spammer(client))

    @app.on_message(admin_filter & filters.command("timer_status", prefixes=["/", ""]))
    async def _timer_status(client: Client, m: Message):
        await m.reply(get_timer_status())

    # Auto scheduler loop trigger on own messages
    @app.on_message(filters.text & filters.me)
    async def _auto_timer(client: Client, message: Message):
        await handle_auto_timer(client, message)

    # Timer config commands
    @app.on_message(admin_filter & filters.command("timer_text", prefixes=["/", ""]))
    async def _timer_text(client: Client, m: Message):
        text = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(set_timer_text(text))

    @app.on_message(admin_filter & filters.command("timer_interval", prefixes=["/", ""]))
    async def _timer_interval(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: timer_interval <minutes>")
        try:
            minutes = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر نیست.")
        await m.reply(set_timer_interval(minutes))

    @app.on_message(admin_filter & filters.command("timer_repeat", prefixes=["/", ""]))
    async def _timer_repeat(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: timer_repeat <count>")
        try:
            count = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر نیست.")
        await m.reply(set_timer_repeat(count))
