# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/forward/forward_commands.py
#
# رجیستر دستورات فوروارد:
#   - saveall <SRC> to <DEST>
#   - add_fmsg / clear_fmsgs
#   - add_ftarget / clear_ftargets
#   - set_fdelay / start_forward / stop_forward / forward_status
#   - (اختیاری) set_fcycle
#
# استفاده در main.py:
#   from SBself.moudels.forward.forward_commands import register as register_forward_commands
#   register_forward_commands(app)

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message
from SBself.filters.SBfilters import admin_filter

# ماژول تک‌فوروارد (saveall) — طبق ساختار زیپ شما زیر modules/forward/
from SBself.modules.forward.forward_cmds import init_forward_tools, forward_all

# ماژول مولتی‌فوروارد (صف پیام‌ها و چند مقصد) — طبق زیپ
from SBself.modules.forward.multi_forward_cmds import (
    add_fmsg, clear_fmsgs,
    add_ftarget, clear_ftargets,
    set_fdelay, set_fcycle,  # set_fcycle اختیاری است؛ اگر در پروژه‌ات نیست حذفش کن
    start_forward, stop_forward, forward_status,
)

def register(app: Client) -> None:
    # آماده‌سازی ابزارهای فوروارد تک‌مقصدی (در صورت نیاز)
    try:
        init_forward_tools(app)
    except Exception:
        # اگر برای اولین بار مسیرها/پوشه‌ها ساخته نشده بود، اجازه بده هندلرها بعداً آن را راه بیندازند
        pass

    @app.on_message(admin_filter & filters.command("saveall", prefixes=["/", ""]))
    async def _saveall(client: Client, m: Message):
        parts = (m.text or "").split()
        if len(parts) < 4 or parts[2].lower() != "to":
            return await m.reply("Usage:\nsaveall <SRC> to <DEST>\nمثال: saveall @somechat to me")
        src, dest = parts[1], parts[3]
        try:
            await m.reply(await forward_all(src, dest))
        except Exception as e:
            await m.reply(f"⚠️ خطا در saveall: {e}")

    # ---- Multi Forwarder ----
    @app.on_message(admin_filter & filters.command("add_fmsg", prefixes=["/", ""]))
    async def _add_fmsg(client: Client, m: Message):
        msg_id = None
        if m.text and len(m.command) > 1:
            try:
                msg_id = int(m.command[1])
            except Exception:
                return await m.reply("❌ msg_id نامعتبر است.")
        await m.reply(await add_fmsg(m, msg_id))

    @app.on_message(admin_filter & filters.command("clear_fmsgs", prefixes=["/", ""]))
    async def _clear_fmsgs(client: Client, m: Message):
        await m.reply(await clear_fmsgs())

    @app.on_message(admin_filter & filters.command("add_ftarget", prefixes=["/", ""]))
    async def _add_ftarget(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: add_ftarget <chat_id|@username>")
        try:
            chat_id = int(m.command[1])
        except Exception:
            chat_id = m.command[1]  # مثلا @channel
        await m.reply(await add_ftarget(chat_id))

    @app.on_message(admin_filter & filters.command("clear_ftargets", prefixes=["/", ""]))
    async def _clear_ftargets(client: Client, m: Message):
        await m.reply(await clear_ftargets())

    @app.on_message(admin_filter & filters.command("set_fdelay", prefixes=["/", ""]))
    async def _set_fdelay(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: set_fdelay <seconds>")
        try:
            seconds = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر وارد کن.")
        await m.reply(await set_fdelay(seconds))

    @app.on_message(admin_filter & filters.command("start_forward", prefixes=["/", ""]))
    async def _start_forward(client: Client, m: Message):
        await m.reply(await start_forward(client))

    @app.on_message(admin_filter & filters.command("stop_forward", prefixes=["/", ""]))
    async def _stop_forward(client: Client, m: Message):
        await m.reply(await stop_forward())

    @app.on_message(admin_filter & filters.command("forward_status", prefixes=["/", ""]))
    async def _forward_status(client: Client, m: Message):
        await m.reply(await forward_status())

    # اختیاری: فاصله‌ی بین چرخه‌ها (اگر در پروژه/ماژولت تعریف نشده، این بلوک را حذف کن)
    @app.on_message(admin_filter & filters.command("set_fcycle", prefixes=["/", ""]))
    async def _set_fcycle(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: set_fcycle <seconds>")
        try:
            seconds = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر وارد کن.")
        await m.reply(await set_fcycle(seconds))
