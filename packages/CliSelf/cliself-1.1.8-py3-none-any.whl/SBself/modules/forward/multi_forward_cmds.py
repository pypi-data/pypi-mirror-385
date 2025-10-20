# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_cmds.py

from typing import Optional, Union
from pyrogram.types import Message
from .multi_forward_manager import MultiForwarder

forwarder = MultiForwarder()

# -------------------------------
# 📌 افزودن پیام (از ریپلای یا msg_id خام)
# -------------------------------
async def add_fmsg(msg: Message, msg_id: Optional[int] = None) -> str:
    """
    اگر روی یک پیام ریپلای شده باشد:
      - اگر forward_from_chat و forward_from_message_id وجود داشت → آیتم در حالت 'forward'
      - در هر حالت، نسخه‌ی محلی (local_chat_id/local_message_id) هم ذخیره می‌شود تا fallback کپی داشته باشیم.
    اگر ریپلای نبود و msg_id دستی دادید → فقط کپی از همان چت فعلی.
    """
    if msg.reply_to_message:
        src = msg.reply_to_message

        # نسخه‌ی محلی برای fallback
        local_chat_id: Union[int, str] = src.chat.id
        local_message_id: int = src.id

        # آیا منبع اصلی فوروارد مشخص است؟
        fchat = getattr(src, "forward_from_chat", None)
        fmsg_id = getattr(src, "forward_from_message_id", None)

        if fchat and fmsg_id:
            # مسیر forward معتبر است
            forwarder.add_item(
                mode="forward",
                forward_chat_id=(getattr(fchat, "id", None) or getattr(fchat, "username", None)),
                forward_message_id=fmsg_id,
                local_chat_id=local_chat_id,
                local_message_id=local_message_id,
            )
            return f"✅ پیام فورواردی ثبت شد (forward) — from {getattr(fchat, 'title', getattr(fchat, 'username', fchat))}, mid={fmsg_id}"
        else:
            # forward بسته بوده یا اطلاعات منبع در دسترس نیست → فقط کپی
            forwarder.add_item(
                mode="copy",
                local_chat_id=local_chat_id,
                local_message_id=local_message_id,
            )
            return f"✅ پیام ثبت شد (copy) — local mid={local_message_id}"

    # بدون ریپلای: msg_id دستی از چت فعلی
    if msg_id is None:
        return "❗ برای ثبت پیام، روی آن ریپلای کن یا msg_id بده."
    forwarder.add_item(
        mode="copy",
        local_chat_id=msg.chat.id,
        local_message_id=msg_id,
    )
    return f"✅ پیام محلی ثبت شد (copy) — mid={msg_id}"

# -------------------------------
# 📌 پاک‌سازی لیست پیام‌ها
# -------------------------------
async def clear_fmsgs() -> str:
    forwarder.clear_items()
    return "🧹 لیست پیام‌ها پاک شد."

# -------------------------------
# 📌 مدیریت تارگت‌ها
# -------------------------------
async def add_ftarget(chat_id: Union[int, str]) -> str:
    forwarder.add_target(chat_id)
    return f"🎯 تارگت `{chat_id}` اضافه شد."

async def clear_ftargets() -> str:
    forwarder.clear_targets()
    return "🧹 لیست تارگت‌ها پاک شد."

# -------------------------------
# 📌 تنظیم سرعت
# -------------------------------
async def set_fdelay(seconds: int) -> str:
    if seconds < 1:
        return "❌ فاصله باید حداقل 1 ثانیه باشد."
    forwarder.set_delay(seconds)
    return f"⏱ فاصله بین ارسال‌ها روی {seconds} ثانیه تنظیم شد."

# -------------------------------
# 📌 عملیات
# -------------------------------
async def start_forward(client) -> str:
    return await forwarder.start(client)

async def stop_forward() -> str:
    return await forwarder.stop()

async def forward_status() -> str:
    return forwarder.status()
