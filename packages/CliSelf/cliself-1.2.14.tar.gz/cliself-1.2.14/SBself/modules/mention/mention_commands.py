
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/mention/mention_commands.py
#
# رجیستر دستورات مدیریت «منشن»
# استفاده در main.py:
#   from SBself.moudels.mention.mention_commands import register as register_mention_commands
#   register_mention_commands(app)

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter
from SBself.config import AllConfig
# بیزنس‌لاجيک منشن
from SBself.modules.mention.mention_manager import (
    set_mention_text,
    set_mention_user,
    toggle_mention,
    add_group,
    remove_group,
    clear_groups,
    mention_status,
)

# اطمینان از وجود ساختار mention در کانفیگ
m_cfg = AllConfig.setdefault("mention", {})
m_cfg.setdefault("textMen", "")
m_cfg.setdefault("useridMen", "")
m_cfg.setdefault("is_menshen", False)
m_cfg.setdefault("group_menshen", False)
m_cfg.setdefault("group_ids", [])

def register(app: Client) -> None:

    @app.on_message(admin_filter & filters.command("setmention", prefixes=["/", ""]))
    async def _setmention(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await set_mention_text(txt))

    @app.on_message(admin_filter & filters.command("mention_user", prefixes=["/", ""]))
    async def _mention_user(client: Client, m: Message):
        if not m.reply_to_message:
            return await m.reply("❗روی پیام فرد هدف ریپلای بزن.")
        user = m.reply_to_message.from_user
        await m.reply(await set_mention_user(user.id))

    @app.on_message(admin_filter & filters.command("mention_toggle", prefixes=["/", ""]))
    async def _mention_toggle(client: Client, m: Message):
        if len(m.command) < 2:
            return await m.reply("Usage: mention_toggle <on|off>")
        enable = (m.command[1].lower() == "on")
        await m.reply(await toggle_mention(enable))

    @app.on_message(admin_filter & filters.command("mention_addgroup", prefixes=["/", ""]))
    async def _mention_addgroup(client: Client, m: Message):
        gid = m.chat.id
        await m.reply(await add_group(gid))

    @app.on_message(admin_filter & filters.command("mention_delgroup", prefixes=["/", ""]))
    async def _mention_delgroup(client: Client, m: Message):
        gid = m.chat.id
        await m.reply(await remove_group(gid))

    @app.on_message(admin_filter & filters.command("mention_cleargroups", prefixes=["/", ""]))
    async def _mention_cleargroups(client: Client, m: Message):
        await m.reply(await clear_groups())

    @app.on_message(admin_filter & filters.command("mention_status", prefixes=["/", ""]))
    async def _mention_status(client: Client, m: Message):
        await m.reply(await mention_status())
