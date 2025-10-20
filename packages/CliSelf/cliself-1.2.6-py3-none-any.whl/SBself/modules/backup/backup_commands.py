# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_commands.py
"""
فرمان‌های بکاپ و ابزارهای جانبی (نسخه منطبق با backup_manager جدید)

دستورات:
- backup on | backup off        (املای backoup هم پذیرفته می‌شود)
- /bk_status
- bk_chat <USER_ID>
- bk_chat <LIMIT> <USER_ID>
  * فقط و فقط با ID کار می‌کند؛ هیچ استفاده‌ای از کانتکست/ریپلای نمی‌شود.
  * USER_ID می‌تواند عددی یا "me" باشد (Saved Messages).
  * LIMIT یعنی تعداد پیام آخر. اگر نیاید یعنی همه.

- get_media <type> <CHAT_ID>
  * type: picture, video, voice, music, video_message, document, gif, sticker
  * CHAT_ID می‌تواند عددی یا "me" باشد.

نحوهٔ اتصال (در main.py، بعد از ساخت app):
    from SBself.modules.backup.backup_commands import register_backup_commands
    register_backup_commands(app)
"""

from __future__ import annotations
import re
import os
import asyncio
from typing import Optional, Tuple, List

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from SBself.config import AllConfig

# --- تلاش برای وارد کردن APIهای موردنیاز از backup_manager ---
# اگر برخی نبود، wrapper داخلی می‌سازیم تا ImportError نگیری.
try:
    from SBself.modules.backup.backup_manager import (
        bk_on as _bk_on,
        bk_off as _bk_off,
        bk_status as _bk_status,
    )
except Exception:
    _bk_on = _bk_off = _bk_status = None

try:
    from SBself.modules.backup.backup_manager import (
        bk_chat_full,         # ذخیره مثل حذف + ساخت خروجی
        log_message,          # ایندکس پیام‌های پرایوت
        on_deleted,           # هوک حذف
        list_media_files,     # لیست فایل‌ها از پوشه‌ی درست
    )
except Exception as e:
    # بدون این‌ها نمی‌توانیم ادامه دهیم
    raise

# --- فیلتر ادمین پروژه: از SBfilters اگر بود؛ وگرنه از کانفیگ ---
try:
    from SBself.filters.SBfilters import admin_filter as _project_admin_filter  # type: ignore
    admin_filter = _project_admin_filter
except Exception:
    _admin_ids = set(AllConfig.get("admin", {}).get("admins", []))
    admin_filter = filters.user(list(_admin_ids)) if _admin_ids else filters.user([])

# ---Fallback wrapperها برای bk_on/bk_off/bk_status اگر در backup_manager نبودند---
if _bk_on is None or _bk_off is None or _bk_status is None:
    async def _bk_on():
        AllConfig.setdefault("backup", {})
        AllConfig["backup"]["bk_enabled"] = True
        return "✅ بکاپ فعال شد."

    async def _bk_off():
        AllConfig.setdefault("backup", {})
        AllConfig["backup"]["bk_enabled"] = False
        return "🛑 بکاپ غیرفعال شد."

    async def _bk_status():
        cfg = AllConfig.setdefault("backup", {})
        return (
            "📊 وضعیت بکاپ:\n"
            f"- enabled: {cfg.get('bk_enabled')}\n"
            f"- db: {cfg.get('bk_db','downloads/backup.db')}\n"
            f"- dir: {cfg.get('bk_dir','downloads/bk_exports')}\n"
            f"- wipe_threshold: {cfg.get('bk_wipe_threshold')}\n"
            f"- wipe_window_minutes: {cfg.get('bk_wipe_window_minutes', 10)}\n"
            f"- cooldown_minutes: {cfg.get('bk_cooldown_minutes', 5)}\n"
        )

# برای یکنواختی نام‌ها
bk_on = _bk_on
bk_off = _bk_off
bk_status = _bk_status


# ---------------------------------
# 🧩 پارس آرگومان‌های bk_chat (فقط با ID)
# ---------------------------------
def _parse_bk_chat_strict(text: str) -> Tuple[Optional[int], Optional[str]]:
    """
    فقط دو الگو مجاز:
      - bk_chat <USER_ID>
      - bk_chat <LIMIT> <USER_ID>

    برمی‌گرداند: (limit, uid_token)
    - limit: تعداد پیام آخر (None = همه)
    - uid_token: "me" یا رشتهٔ عددی (همان‌طور که هست؛ تبدیل به int در هندلر انجام می‌شود)

    اگر قالب معتبر نباشد → (None, None)
    """
    parts = (text or "").strip().split()
    if not parts:
        return None, None
    cmd = parts[0].lower()
    if cmd not in ("bk_chat", "/bk_chat"):
        return None, None
    args = parts[1:]

    if len(args) == 1:
        # فقط USER_ID
        uid_token = args[0]
        return None, uid_token

    if len(args) == 2:
        # LIMIT + USER_ID
        if not re.fullmatch(r"\d+", args[0]):
            return None, None
        limit = int(args[0])
        uid_token = args[1]
        return limit, uid_token

    return None, None


async def _resolve_uid_token(client, uid_token: str) -> Optional[int]:
    """
    uid_token می‌تواند "me" یا یک عدد باشد.
    اگر "me" بود، به id خود کاربر تبدیل می‌شود؛ اگر عدد بود، int آن.
    """
    if uid_token is None:
        return None
    t = uid_token.strip().lower()
    if t == "me":
        me = await client.get_me()
        return int(me.id)
    # فقط عدد مثبت/منفی؟
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except Exception:
            return None
    return None


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
        if not os.path.isfile(path):
            return False

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
            await client.send_document(chat_id, path, reply_to_message_id=reply_to)
            return True

    except Exception:
        # fallback: حداقل به صورت document ارسال شود
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

    # 3) bk_chat: فقط با ID؛ هیچ برداشت از کانتکست/ریپلای انجام نمی‌شود
    @app.on_message(admin_filter & filters.regex(r"^(?:/?bk_chat)(?:\s+.+)?$", flags=re.IGNORECASE))
    async def _bk_chat_cmd(client, m: Message):
        limit, uid_tok = _parse_bk_chat_strict(m.text or "")
        if uid_tok is None:
            return await m.reply(
                "❗ قالب درست:\n"
                "`bk_chat <USER_ID>` یا `bk_chat <LIMIT> <USER_ID>`\n"
                "نکته: USER_ID می‌تواند عدد یا `me` باشد. هیچ برداشت خودکاری از کانتکست انجام نمی‌شود."
            )

        uid = await _resolve_uid_token(client, uid_tok)
        if uid is None:
            return await m.reply("❗ USER_ID نامعتبر است. از عدد یا `me` استفاده کن.")

        # اجرای بکاپ دقیقاً برای همان ID
        saved_count, path = await bk_chat_full(client, uid, limit=limit, send_to_saved=False)

        if not path:
            return await m.reply(
                f"⚠️ بکاپ برای چت `{uid}` انجام شد (ذخیره {saved_count} پیام)، "
                "اما فایل خروجی ساخته نشد."
            )

        caption = f"📦 Backup of {uid} ({'all' if not limit else f'last {limit}'})\nSaved: {saved_count}"
        # ارسال به Saved Messages (اختیاری)
        try:
            await client.send_document("me", path, caption=caption)
        except Exception:
            pass
        # پاسخ در همان چت فرمان‌دهنده
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
        # اگر decorator در نسخه Pyrogram شما موجود نباشد، قابل صرف‌نظر است.
        pass

    # 6) get_media <type> <CHAT_ID>  (CHAT_ID می‌تواند "me" باشد)
    VALID_TYPES = {"picture", "video", "voice", "music", "video_message", "document", "gif", "sticker"}

    @app.on_message(admin_filter & filters.regex(r"^(?:/?)(?:get_media)\s+(\w+)\s+(\S+)\s*$", flags=re.IGNORECASE))
    async def _get_media_cmd(client, m: Message):
        media_type = m.matches[0].group(1).lower()
        uid_tok = m.matches[0].group(2)

        # نرمال‌سازی
        if media_type in {"anim", "animation"}:
            media_type = "gif"
        if media_type == "audio":
            media_type = "music"

        if media_type not in VALID_TYPES:
            return await m.reply("❗ نوع مدیا معتبر نیست. مجازها: " + ", ".join(sorted(VALID_TYPES)))

        target_chat_id = await _resolve_uid_token(client, uid_tok)
        if target_chat_id is None:
            return await m.reply("❗ CHAT_ID نامعتبر است. از عدد یا `me` استفاده کن.")

        files: List[str] = list_media_files(target_chat_id, media_type)

        # Fallback کوچک برای سازگاری با خروجی‌های قدیمی (در صورت نیاز):
        if media_type == "gif" and not files:
            doc_files = list_media_files(target_chat_id, "document")
            doc_gifs = [p for p in doc_files if p.lower().endswith((".gif", ".mp4", ".webm"))]
            if doc_gifs:
                files = doc_gifs

        if not files:
            return await m.reply(f"⚠️ فایلی برای `{media_type}` در چت {target_chat_id} پیدا نشد.")

        sent = 0
        failed = 0
        for p in files:
            ok = await _send_media_smart(client, m.chat.id, media_type, p, reply_to=m.id)
            if ok:
                sent += 1
            else:
                failed += 1
            await asyncio.sleep(0.25)  # جلوگیری از FloodWait

        if failed == 0:
            await m.reply(f"✅ {sent} فایل `{media_type}` از چت {target_chat_id} ارسال شد.")
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
