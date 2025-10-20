# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_commands.py
"""
فرمان‌های بکاپ + ارسال مدیاهای ذخیره‌شده.
- backup on/off (حتی backoup)
- /bk_status
- /bk_chat  [101] [USERID]
- get_media <type> <CHAT_ID>   ← جدید
"""

from __future__ import annotations
import re
import asyncio
import os
from typing import Optional, Tuple

from pyrogram import filters
from pyrogram.types import Message

from SBself.config import AllConfig
from SBself.modules.backup.backup_manager import (
    bk_on, bk_off, bk_status,
    bk_export_dialog_for_user, bk_export_dialog_from_db,
    log_message, on_deleted,
    list_media_files
)

# استفاده از فیلترهای پروژه (بدون بازنویسی)
try:
    from SBself.filters.SBfilters import admin_filter as _project_admin_filter  # type: ignore
    admin_filter = _project_admin_filter
except Exception:
    _admin_ids = set(AllConfig.get("admin", {}).get("admins", []))
    admin_filter = filters.user(list(_admin_ids)) if _admin_ids else filters.user([])


def _parse_bk_chat_args(text: str, m: Message) -> Tuple[Optional[int], Optional[int]]:
    parts = (text or "").strip().split()
    if parts and parts[0].lower().startswith(("bk_chat", "/bk_chat")):
        parts = parts[1:]

    nums = [p for p in parts if re.fullmatch(r"-?\d+", p)]
    limit: Optional[int] = None
    uid: Optional[int] = None

    if len(nums) >= 2:
        limit = int(nums[0]); uid = int(nums[1])
    elif len(nums) == 1:
        n = int(nums[0])
        # اگر در context مشخص نیست، به عنوان USERID تفسیر کن
        if (m.chat and m.chat.type.name.lower() == "private") or m.reply_to_message:
            limit = n
        else:
            uid = n

    if uid is None:
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat and m.chat.type.name.lower() == "private":
            uid = m.chat.id

    return limit, uid


# -----------------------------
# ثبت هندلرها
# -----------------------------
def register_backup_commands(app):
    # backup on/off
    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:backup|backoup)\s+(on|off)\s*$", flags=re.IGNORECASE))
    async def _backup_toggle_text(_, m: Message):
        mode = m.matches[0].group(1).lower()
        await m.reply(await (bk_on() if mode == "on" else bk_off()))

    # bk_status
    @app.on_message(admin_filter & filters.command(["bk_status"], prefixes=["/", ""]))
    async def _bk_status_cmd(_, m: Message):
        await m.reply(await bk_status())

    # bk_chat
    @app.on_message(admin_filter & filters.command(["bk_chat"], prefixes=["/", ""]))
    async def _bk_chat_cmd(client, m: Message):
        limit, uid = _parse_bk_chat_args(m.text or "", m)
        if uid is None:
            return await m.reply(
                "❗ باید روی پیام طرف ریپلای کنی، داخل پی‌وی خودش باشی، یا USERID بدی.\n"
                "الگوها: `bk_chat 101` | `bk_chat 101 USERID` | `bk_chat USERID`"
            )
        path = await bk_export_dialog_for_user(client, uid, limit=limit)
        if not path:
            # اگر از API چیزی نبود، از DB تلاش کن
            path = await bk_export_dialog_from_db(client, uid, limit=limit)
        if not path:
            return await m.reply("⚠️ چیزی برای بکاپ پیدا نشد.")

        await client.send_document("me", path, caption=f"📦 Backup of {uid} ({'all' if not limit else f'last {limit}'})")
        await m.reply_document(path, caption="📦 Backup ready.")

    # لاگ پیام‌های private
    @app.on_message(filters.private, group=50)
    async def _index_private_messages(_, m: Message):
        await log_message(m)

    # واکنش به حذف‌ها
    try:
        @app.on_deleted_messages(filters.private)
        async def _on_deleted_private(client, deleted):
            await on_deleted(client, deleted)
    except Exception:
        pass

    # -----------------------------
    # get_media <type> <CHAT_ID>
    # -----------------------------
    VALID_TYPES = {"picture", "video", "voice", "music", "video_message", "document", "gif", "sticker"}

    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:get_media)\s+(\w+)\s+(-?\d+)\s*$", flags=re.IGNORECASE))
    async def _get_media_cmd(client, m: Message):
        media_type = m.matches[0].group(1).lower()
        try:
            chat_id = int(m.matches[0].group(2))
        except Exception:
            return await m.reply("❗ فرمت درست: `get_media <type> <CHAT_ID>`")

        if media_type not in VALID_TYPES:
            return await m.reply("❗ نوع مدیا معتبر نیست. موارد مجاز: " + ", ".join(sorted(VALID_TYPES)))

        files = list_media_files(chat_id, media_type)
        if not files:
            return await m.reply(f"⚠️ فایلی برای `{media_type}` در چت {chat_id} پیدا نشد.")

        # برای جلوگیری از اسپم تلگرام، یکی‌یکی یا در بسته‌های کوچک ارسال کن
        sent = 0
        for p in files:
            try:
                await client.send_document(m.chat.id, p)
                sent += 1
            except Exception as e:
                await m.reply(f"🚫 ارسال {os.path.basename(p)} ناموفق بود: {e}")
            # استراحت کوتاه بین ارسال‌ها
            await asyncio.sleep(0.3)

        await m.reply(f"✅ {sent} فایل `{media_type}` از چت {chat_id} ارسال شد.")

    # لاگ
    try:
        from SBself.modules.backup.backup_manager import logger
        logger.info("backup_commands registered (with get_media).")
    except Exception:
        pass
