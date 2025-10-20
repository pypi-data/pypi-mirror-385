# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_cmds.py

from typing import Union, Optional
from pyrogram.types import Message
from .multi_forward_manager import MultiForwarder

forwarder = MultiForwarder()

# -------------------------------
# 📌 افزودن پیام (فقط فوروارد)
# -------------------------------
async def add_fmsg(msg: Message, _unused: Optional[int] = None) -> str:
    """
    فقط وقتی قبول می‌کنیم که روی یک پیام فورواردشده ریپلای شود و
    forward_from_chat + forward_from_message_id در دسترس باشند.
    """
    if not msg.reply_to_message:
        return "❗ برای ثبت پیام، حتماً روی **پیامِ فورواردشده از کانال** ریپلای کن."

    src = msg.reply_to_message
    fchat = getattr(src, "forward_from_chat", None)
    fmsg_id = getattr(src, "forward_from_message_id", None)

    if not (fchat and fmsg_id):
        return "❌ این پیام منبع فوروارد معتبری ندارد. لطفاً روی پیام فورواردشده از کانال ریپلای کن."

    forward_chat_id: Union[int, str] = getattr(fchat, "id", None) or getattr(fchat, "username", None)
    if forward_chat_id is None:
        return "❌ شناسه‌ی منبع فوروارد در دسترس نیست."

    forwarder.add_item(forward_chat_id=forward_chat_id, forward_message_id=int(fmsg_id))
    return f"✅ پیام ثبت شد (forward): from={forward_chat_id}, mid={fmsg_id}"

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
# 📌 تنظیم سرعت‌ها
# -------------------------------
async def set_fdelay(seconds: int) -> str:
    if seconds < 1:
        return "❌ فاصله باید حداقل 1 ثانیه باشد."
    forwarder.set_delay(seconds)
    return f"⏱ فاصله بین ارسال‌ها روی {seconds} ثانیه تنظیم شد."

async def set_fcycle(seconds: int) -> str:
    if seconds < 0:
        return "❌ مقدار نامعتبر است."
    forwarder.set_cycle_delay(seconds)
    return f"🔁 فاصله بین دورها روی {seconds} ثانیه تنظیم شد."

# -------------------------------
# 📌 عملیات
# -------------------------------
async def start_forward(client) -> str:
    return await forwarder.start(client)

async def stop_forward() -> str:
    return await forwarder.stop()

async def forward_status() -> str:
    return forwarder.status()
