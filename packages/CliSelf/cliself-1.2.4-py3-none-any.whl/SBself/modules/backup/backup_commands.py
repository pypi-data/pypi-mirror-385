# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_commands.py
"""
فرمان‌های بکاپ و ابزارهای جانبی:

دستورات:
- backup on | backup off        (املای backoup هم پذیرفته می‌شود)
- /bk_status
- /bk_chat [LIMIT] [USERID]     → سه الگو:
      bk_chat 101
      bk_chat 101 USERID
      bk_chat USERID
- get_media <type> <CHAT_ID>    → type یکی از: picture, video, voice, music, video_message, document, gif, sticker

نحوهٔ اتصال (در main.py، بعد از ساخت app):
    from SBself.modules.backup.backup_commands import register_backup_commands
    register_backup_commands(app)
"""

from __future__ import annotations
import re
import os
import asyncio
from typing import Optional, Tuple

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from SBself.config import AllConfig
from SBself.modules.backup.backup_manager import (
    bk_on, bk_off, bk_status,
    bk_export_dialog_for_user, bk_export_dialog_from_db,  # برای سازگاری؛ فعلاً استفاده نمی‌کنیم
    bk_chat_full,  # استفاده می‌کنیم تا دقیقاً مثل حذف بکاپ بگیرد + خروجی بسازد
    log_message, on_deleted,
    list_media_files,
)

# ---------------------------------
# 🔐 فیلتر ادمین پروژه (بدون بازنویسی)
# ---------------------------------
try:
    # اگر پروژه فیلتر اختصاصی ادمین داشته باشد از همان استفاده می‌کنیم
    from SBself.filters.SBfilters import admin_filter as _project_admin_filter  # type: ignore
    admin_filter = _project_admin_filter
except Exception:
    # fallback: از لیست ادمین‌ها در کانفیگ
    _admin_ids = set(AllConfig.get("admin", {}).get("admins", []))
    admin_filter = filters.user(list(_admin_ids)) if _admin_ids else filters.user([])

# ---------------------------------
# 🧩 پارس آرگومان‌های bk_chat
# ---------------------------------
def _parse_bk_chat_args(text: str, m: Message) -> Tuple[Optional[int], Optional[int]]:
    """
    خروجی: (limit, user_id)
      - bk_chat 101              → limit=101, user از context (private یا ریپلای)
      - bk_chat 101 USERID      → limit=101, user=USERID
      - bk_chat USERID          → limit=None (فول), user=USERID
    """
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
        # اگر داخل private یا ریپلای هستیم، این عدد را limit درنظر بگیر؛
        # در غیر این صورت، آن را USERID فرض کن.
        if (m.chat and m.chat.type == ChatType.PRIVATE) or m.reply_to_message:
            limit = n
        else:
            uid = n

    # اگر uid از context مشخص نیست، از ریپلای/پرایوت بگیر
    if uid is None:
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat and m.chat.type == ChatType.PRIVATE:
            uid = m.chat.id

    return limit, uid

# ---------------------------------
# 🚚 ارسال فایل با نوع مناسب
# ---------------------------------
async def _send_media_smart(client, chat_id: int, media_type: str, path: str, reply_to: Optional[int] = None) -> bool:
    """
    بسته به نوع مدیا، بهترین متد ارسال تلگرام را انتخاب می‌کند.
    اگر شکست خورد، به send_document برمی‌گردد.
    """
    media_type = (media_type or "").lower()
    try:
        if media_type == "picture":
            await client.send_photo(chat_id, path, reply_to_message_id=reply_to)
            return True
        elif media_type in ("video", "gif", "video_message"):
            # GIFهای ما mp4 هستند و باید به‌صورت ویدئو ارسال شوند.
            await client.send_video(chat_id, path, supports_streaming=True, reply_to_message_id=reply_to)
            return True
        elif media_type == "voice":
            await client.send_voice(chat_id, path, reply_to_message_id=reply_to)
            return True
        elif media_type in ("music", "audio"):
            await client.send_audio(chat_id, path, reply_to_message_id=reply_to)
            return True
        elif media_type == "sticker":
            await client.send_sticker(chat_id, path, reply_to_message_id=reply_to)
            return True
        elif media_type == "document":
            await client.send_document(chat_id, path, reply_to_message_id=reply_to)
            return True
        else:
            # ناشناخته → داکیومنت
            await client.send_document(chat_id, path, reply_to_message_id=reply_to)
            return True
    except Exception:
        # fallback
        try:
            await client.send_document(chat_id, path, reply_to_message_id=reply_to)
            return True
        except Exception:
            return False

# ---------------------------------
# 🔌 ثبت هندلرها
# ---------------------------------
def register_backup_commands(app):
    """
    این تابع را در main.py صدا بزن تا فرمان‌ها و هوک‌ها فعال شوند.
    """

    # 1) backup on/off  (backoup هم پشتیبانی)
    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:backup|backoup)\s+(on|off)\s*$", flags=re.IGNORECASE))
    async def _backup_toggle_text(_, m: Message):
        mode = m.matches[0].group(1).lower()
        await m.reply(await (bk_on() if mode == "on" else bk_off()))

    # 2) /bk_status
    @app.on_message(admin_filter & filters.command(["bk_status"], prefixes=["/", ""]))
    async def _bk_status_cmd(_, m: Message):
        await m.reply(await bk_status())

    # 3) /bk_chat  → بکاپی که دقیقاً مثل حذف ذخیره می‌کند، سپس خروجی می‌سازد و می‌فرستد
    @app.on_message(admin_filter & filters.command(["bk_chat"], prefixes=["/", ""]))
    async def _bk_chat_cmd(client, m: Message):
        limit, uid = _parse_bk_chat_args(m.text or "", m)
        if uid is None:
            return await m.reply(
                "❗ باید روی پیام طرف ریپلای کنی، داخل پی‌وی خودش باشی، یا USERID بدی.\n"
                "الگوها: `bk_chat 101` | `bk_chat 101 USERID` | `bk_chat USERID`"
            )

        saved_count, path = await bk_chat_full(client, uid, limit=limit, send_to_saved=False)

        if not path:
            return await m.reply(f"⚠️ بکاپ انجام شد (ذخیره {saved_count} پیام)، ولی فایلی برای ارسال ساخته نشد.")

        caption = f"📦 Backup of {uid} ({'all' if not limit else f'last {limit}'})\nSaved: {saved_count}"
        # ارسال به Saved Messages
        try:
            await client.send_document("me", path, caption=caption)
        except Exception:
            pass
        # پاسخ در همان چت
        await m.reply_document(path, caption="📦 Backup ready.")

    # 4) ایندکس پیام‌های private برای ثبت در DB + ذخیرهٔ مدیا
    @app.on_message(filters.private, group=50)
    async def _index_private_messages(_, m: Message):
        await log_message(m)

    # 5) واکنش به حذف پیام‌ها (تشخیص wipe)
    try:
        @app.on_deleted_messages(filters.private)
        async def _on_deleted_private(client, deleted):
            await on_deleted(client, deleted)
    except Exception:
        # اگر نسخهٔ Pyrogram قدیمی باشد و decorator موجود نباشد، قابل صرف‌نظر است.
        pass

    # 6) get_media <type> <CHAT_ID>
    VALID_TYPES = {"picture", "video", "voice", "music", "video_message", "document", "gif", "sticker"}

    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:get_media)\s+(\w+)\s+(-?\d+)\s*$", flags=re.IGNORECASE))
    async def _get_media_cmd(client, m: Message):
        media_type = m.matches[0].group(1).lower()
        try:
            chat_id = int(m.matches[0].group(2))
        except Exception:
            return await m.reply("❗ فرمت درست: `get_media <type> <CHAT_ID>`")

        # نرمال‌سازی چند نام مترادف
        if media_type in {"anim", "animation"}:
            media_type = "gif"
        if media_type == "audio":
            media_type = "music"

        if media_type not in VALID_TYPES:
            return await m.reply("❗ نوع مدیا معتبر نیست. مجازها: " + ", ".join(sorted(VALID_TYPES)))

        files = list_media_files(chat_id, media_type)
        if not files:
            return await m.reply(f"⚠️ فایلی برای `{media_type}` در چت {chat_id} پیدا نشد.")

        sent = 0
        failed = 0
        # برای جلوگیری از FloodWait فاصلهٔ کوتاه می‌گذاریم
        for p in files:
            ok = await _send_media_smart(client, m.chat.id, media_type, p, reply_to=m.id)
            if ok:
                sent += 1
            else:
                failed += 1
            await asyncio.sleep(0.25)

        if failed == 0:
            await m.reply(f"✅ {sent} فایل `{media_type}` از چت {chat_id} ارسال شد.")
        elif sent == 0:
            await m.reply(f"🚫 هیچ فایلی از نوع `{media_type}` نتوانستم بفرستم (همه شکست خورد).")
        else:
            await m.reply(f"⚠️ {sent} فایل ارسال شد، {failed} مورد ناموفق بود.")

    # لاگ ثبت موفق
    try:
        from SBself.modules.backup.backup_manager import logger
        logger.info("backup_commands registered.")
    except Exception:
        pass
