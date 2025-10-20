# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_commands.py
"""
هندلر فرمان‌ها و رویدادهای بکاپ.
- backup on/off  (حتی backoup)
- /bk_status
- /bk_chat  [101] [USERID]
- لاگ پیام‌های private + واکنش به حذف‌ها (wipe → بکاپ خودکار)

نحوه‌ی اتصال در main.py (بعد از ساخت app):
    from SBself.modules.backup.backup_commands import register_backup_commands
    register_backup_commands(app)
"""

from __future__ import annotations
import re
from typing import Optional, Tuple

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from SBself.config import AllConfig
from SBself.modules.backup.backup_manager import (
    bk_on, bk_off, bk_status,
    bk_export_dialog_for_user,
    log_message, on_deleted,
)

# ---------------------------------
# 🔐 دریافت فیلتر ادمین از پروژه (بدون بازنویسی)
# ---------------------------------
# تلاش برای استفاده از فیلترهای داخلی پروژه؛ اگر در دسترس نبودند، fallback سبک
try:
    # سعی می‌کنیم از فیلترهای خود پروژه استفاده کنیم
    from SBself.filters.SBfilters import admin_filter as _project_admin_filter  # type: ignore
    admin_filter = _project_admin_filter
except Exception:
    # fallback: بر اساس AllConfig.admin.admins
    _admin_ids = set(AllConfig.get("admin", {}).get("admins", []))
    admin_filter = filters.user(list(_admin_ids)) if _admin_ids else filters.user([])


# ---------------------------------
# 🧩 پارس آرگومان‌های bk_chat
# ---------------------------------
def _parse_bk_chat_args(text: str, m: Message) -> Tuple[Optional[int], Optional[int]]:
    """
    خروجی: (limit, user_id)
    قواعد:
      - bk_chat 101              → limit=101, uid از context (چت private جاری یا ریپلای)
      - bk_chat 101 USERID      → limit=101, uid=USERID
      - bk_chat USERID          → limit=None (همه), uid=USERID
    """
    parts = (text or "").strip().split()
    if parts and parts[0].lower().startswith(("bk_chat", "/bk_chat")):
        parts = parts[1:]

    nums = [p for p in parts if re.fullmatch(r"-?\d+", p)]
    limit: Optional[int] = None
    uid: Optional[int] = None

    if len(nums) >= 2:
        limit = int(nums[0])
        uid = int(nums[1])
    elif len(nums) == 1:
        # ممکن است عددِ limit یا USERID باشد؛ بر اساس context تشخیص بده
        n = int(nums[0])
        if (m.chat and m.chat.type == ChatType.PRIVATE) or m.reply_to_message:
            # context مشخص است → این عدد را limit فرض کن
            limit = n
        else:
            # context نامشخص → این عدد را USERID فرض کن
            uid = n

    # اگر uid هنوز مشخص نیست از context بگیر
    if uid is None:
        if m.reply_to_message and m.reply_to_message.from_user:
            uid = m.reply_to_message.from_user.id
        elif m.chat and m.chat.type == ChatType.PRIVATE:
            uid = m.chat.id

    return limit, uid


# ---------------------------------
# 🔌 ثبت هندلرها
# ---------------------------------
def register_backup_commands(app):
    """
    این تابع را در main.py صدا بزن تا فرمان‌ها/هوک‌های بکاپ فعال شوند.
    """

    # 1) backup on/off  (حتی backoup)
    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:backup|backoup)\s+(on|off)\s*$", flags=re.IGNORECASE))
    async def _backup_toggle_text(_, m: Message):
        mode = m.matches[0].group(1).lower()
        if mode == "on":
            await m.reply(await bk_on())
        else:
            await m.reply(await bk_off())

    # 2) /bk_status
    @app.on_message(admin_filter & filters.command(["bk_status"], prefixes=["/", ""]))
    async def _bk_status_cmd(_, m: Message):
        await m.reply(await bk_status())

    # 3) /bk_chat
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
            return await m.reply("⚠️ چیزی برای بکاپ پیدا نشد.")

        # ارسال به Saved Messages + اطلاع در چت جاری
        cap = f"📦 Backup of {uid} ({'all' if not limit else f'last {limit}'})"
        await client.send_document("me", path, caption=cap)
        await m.reply_document(path, caption="📦 Backup ready.")

    # 4) لاگ پیام‌های private (برای ریکاوری/گزارش حذف)
    @app.on_message(filters.private, group=50)
    async def _index_private_messages(_, m: Message):
        await log_message(m)

    # 5) واکنش به حذف پیام‌ها (تشخیص wipe و بکاپ خودکار)
    # Pyrogram v2: on_deleted_messages
    try:
        @app.on_deleted_messages(filters.private)
        async def _on_deleted_private(client, deleted):
            await on_deleted(client, deleted)
    except Exception:
        # برای نسخه‌های قدیمی‌تر Pyrogram کاربر می‌تواند این قسمت را نگاشت کند.
        pass

    # لاگ ثبت موفق
    try:
        from SBself.modules.backup.backup_manager import logger
        logger.info("backup_commands registered.")
    except Exception:
        pass
