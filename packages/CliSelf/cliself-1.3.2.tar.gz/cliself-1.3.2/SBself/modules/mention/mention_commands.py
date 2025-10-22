# -*- coding: utf-8 -*-
# File: SBself/modules/mention/mention_commands.py
#
# رجیستر دستورات مدیریت «منشن»
# استفاده در main.py:
#   from SBself.modules.mention.mention_commands import register as register_mention_commands
#   register_mention_commands(app)

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied

from SBself.filters.SBfilters import admin_filter
from SBself.config import AllConfig

# بیزنس‌لاجیک منشن
from SBself.modules.mention.mention_manager import (
    set_mention_text,
    set_mention_user,
    toggle_mention,           # تکی: on/off
    toggle_group_mention,     # گروهی: on/off
    add_groups_by_ids,        # افزودن چند ID یکجا
    add_group_from_reply,     # افزودن از روی ریپلای
    remove_groups_by_ids,     # حذف چند ID یکجا
    clear_groups,             # پاکسازی کامل
    mention_status,
)

# اطمینان از وجود ساختار mention در کانفیگ
m_cfg = AllConfig.setdefault("mention", {})
m_cfg.setdefault("textMen", "")
m_cfg.setdefault("useridMen", "")
m_cfg.setdefault("is_menshen", False)
m_cfg.setdefault("group_menshen", False)
m_cfg.setdefault("group_ids", [])


# ================================
# Helpers
# ================================

async def _resolve_one_token_to_id(client: Client, token: str) -> Optional[int]:
    """
    token را به chat/user id عددی تبدیل می‌کند:
      - "me" → id خود اکانت
      - "-100..." یا عدد → همان int
      - "@username" یا "t.me/username" → get_chat → id
    اگر نتوانست، None.
    """
    if token is None:
        return None
    t = token.strip()
    if not t:
        return None

    # me
    if t.lower() == "me":
        me = await client.get_me()
        return int(me.id)

    # عدد
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except Exception:
            return None

    # username / لینک
    username = t
    if username.startswith("@"):
        username = username[1:]
    if "t.me/" in username.lower():
        username = re.sub(r"^https?://t\.me/", "", username, flags=re.IGNORECASE).strip("/")

    try:
        ch = await client.get_chat(username)
        return int(ch.id)
    except (UsernameNotOccupied, Exception):
        return None


async def _resolve_many_tokens_to_ids(client: Client, tokens: List[str]) -> List[int]:
    """لیست توکن‌ها را به لیست ID عددی تبدیل می‌کند (تبدیل‌های ناموفق حذف می‌شوند)."""
    out: List[int] = []
    for tok in tokens:
        cid = await _resolve_one_token_to_id(client, tok)
        if cid is not None:
            out.append(cid)
    return out


# ================================
# Register Commands
# ================================

def register(app: Client) -> None:
    # -----------------------------
    # متن و منشن تکی
    # -----------------------------
    @app.on_message(admin_filter & filters.command("setmention", prefixes=["/", ""]))
    async def _setmention(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await set_mention_text(txt))

    @app.on_message(admin_filter & filters.command("mention_user", prefixes=["/", ""]))
    async def _mention_user(client: Client, m: Message):
        if not m.reply_to_message or not m.reply_to_message.from_user:
            return await m.reply("❗روی پیام فرد هدف ریپلای بزن.")
        user = m.reply_to_message.from_user
        await m.reply(await set_mention_user(user.id))

    @app.on_message(admin_filter & filters.command("mention_toggle", prefixes=["/", ""]))
    async def _mention_toggle(client: Client, m: Message):
        if len(m.command) < 2:
            return await m.reply("Usage: /mention_toggle <on|off>")
        enable = (m.command[1].lower() == "on")
        await m.reply(await toggle_mention(enable))

    # -----------------------------
    # منشن گروهی (روشن/خاموش)
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_group_toggle", prefixes=["/", ""]))
    async def _mention_group_toggle(client: Client, m: Message):
        if len(m.command) < 2:
            return await m.reply("Usage: /mention_group_toggle <on|off>")
        enable = (m.command[1].lower() == "on")
        await m.reply(await toggle_group_mention(enable))

    # -----------------------------
    # افزودن گروهی ID ها به ترتیب داده‌شده
    # مثال: /mention_gps id1 id2 id3 ...
    # (me / @username / t.me/username / عدد پشتیبانی می‌شود)
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_gps", prefixes=["/", ""]))
    async def _mention_gps(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /mention_gps <id1> <id2> ...")
        tokens = m.command[1:]
        ids = await _resolve_many_tokens_to_ids(client, tokens)
        if not ids:
            return await m.reply("❌ هیچ شناسهٔ معتبری تشخیص داده نشد.")
        msg = await add_groups_by_ids(*ids)
        await m.reply(msg)

    # -----------------------------
    # افزودن از روی ریپلای (کاربرِ ریپلای → group_ids)
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_gps_reply", prefixes=["/", ""]))
    async def _mention_gps_reply(client: Client, m: Message):
        if not m.reply_to_message or not m.reply_to_message.from_user:
            return await m.reply("❗روی پیام فرد هدف ریپلای بزن.")
        uid = int(m.reply_to_message.from_user.id)
        msg = await add_group_from_reply(uid)
        await m.reply(msg)

    # -----------------------------
    # حذف یک/چند ID از group_ids
    # مثال: /mention_del id1 id2 ...
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_del", prefixes=["/", ""]))
    async def _mention_del(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /mention_del <id1> <id2> ...")
        tokens = m.command[1:]
        ids = await _resolve_many_tokens_to_ids(client, tokens)
        if not ids:
            return await m.reply("❌ هیچ شناسهٔ معتبری برای حذف تشخیص داده نشد.")
        msg = await remove_groups_by_ids(*ids)
        await m.reply(msg)

    # -----------------------------
    # پاکسازی کامل group_ids
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_clear", prefixes=["/", ""]))
    async def _mention_clear(client: Client, m: Message):
        await m.reply(await clear_groups())

    # -----------------------------
    # وضعیت
    # -----------------------------
    @app.on_message(admin_filter & filters.command("mention_status", prefixes=["/", ""]))
    async def _mention_status(client: Client, m: Message):
        await m.reply(await mention_status())

    # # -----------------------------
    # # aliasهای کاربردی (اختیاری): افزودن/حذف چت فعلی
    # # -----------------------------
    # @app.on_message(admin_filter & filters.command("mention_add_here", prefixes=["/", ""]))
    # async def _mention_add_here(client: Client, m: Message):
    #     # چت جاری را به لیست گروهی اضافه کن
    #     msg = await add_groups_by_ids(m.chat.id)
    #     await m.reply(msg)

    # @app.on_message(admin_filter & filters.command("mention_del_here", prefixes=["/", ""]))
    # async def _mention_del_here(client: Client, m: Message):
    #     msg = await remove_groups_by_ids(m.chat.id)
    #     await m.reply(msg)
