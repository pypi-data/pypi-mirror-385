# -*- coding: utf-8 -*-
# File: SBself/modules/get_code/get_code_command.py
#
# وظیفه: آخرین پیام از چت 777000 (Service Notifications) را بگیرد
#        و در مسیر پروژه داخل "downloads/code.txt" بنویسد (هر بار جایگزین می‌شود). 

from pathlib import Path
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

# اگر می‌خواهی فقط مدیرها بتوانند استفاده کنند، این را فعال کن
from SBself.filters.SBfilters import admin_filter , owner_admin_only
from SBself.core.edit_and_reply import _edit_or_reply

# ------------------------------
# ابزارهای داخلی
# ------------------------------
def _downloads_file_path() -> Path:
    # مسیر فایل هدف: downloads/code.txt در روت پروژه (cwd اجرای برنامه)
    downloads = Path("downloads")
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads / "code.txt"


async def _get_last_message_text(client: Client, chat_id: int) -> Optional[str]:
    """
    آخرین پیام را از chat_id می‌گیرد و متن/کپشن آن را برمی‌گرداند.
    با Pyrogram v2 و v1 سازگار (تلاش چندگانه).
    """
    # تلاش 1: history iterator (Pyrogram v2)
    try:
        async for msg in client.get_chat_history(chat_id, limit=1):
            if msg:
                return (msg.text or msg.caption or "").strip() or None
    except AttributeError:
        # متد موجود نیست → می‌رویم سراغ تلاش بعدی
        pass
    except Exception:
        # هر خطایی، تلاش بعدی
        pass

    # تلاش 2: get_history (در برخی نسخه‌ها لیست برمی‌گرداند)
    try:
        hist = await client.get_history(chat_id, limit=1)  # type: ignore
        if hist:
            msg = hist[0]
            return (msg.text or msg.caption or "").strip() or None
    except Exception:
        pass

    # تلاش 3: iter از تاریخ (برخی نسخه‌ها: iter_history / search_messages)
    try:
        # بعضی نسخه‌ها متدی به‌نام search_messages دارند که از آخر به اول نیست،
        # اما برای دریافت نزدیک‌ترین پیام می‌توان limit=1 زد.
        async for msg in client.search_messages(chat_id, limit=1):  # type: ignore
            if msg:
                return (msg.text or msg.caption or "").strip() or None
    except Exception:
        pass

    return None


# ------------------------------
# API اصلی
# ------------------------------
async def save_latest_code_from_777000(client: Client) -> str:
    """
    آخرین پیام چت 777000 را گرفته و در downloads/code.txt می‌نویسد (overwrite).
    خروجی یک پیام وضعیت است.
    """
    chat_id = 777000
    text = await _get_last_message_text(client, chat_id)
    if not text:
        return "❌ پیامی برای ذخیره‌سازی یافت نشد."

    path = _downloads_file_path()
    try:
        path.write_text(text, encoding="utf-8")
        return f"✅ آخرین پیام 777000 ذخیره شد: {path.as_posix()}"
    except Exception as e:
        return f"❌ خطا در نوشتن فایل: {e}"


def register(app: Client) -> None:
    @app.on_message(owner_admin_only & filters.command("get_code", prefixes=["/", ""]))
    async def _get_code_cmd(client: Client, m: Message):
        await save_latest_code_from_777000(client) 
