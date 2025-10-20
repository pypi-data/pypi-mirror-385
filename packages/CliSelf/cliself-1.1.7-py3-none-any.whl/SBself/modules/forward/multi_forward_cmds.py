# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_cmds.py

from pyrogram.types import Message
from .multi_forward_manager import MultiForwarder

# نمونه عمومی Forwarder (میتونی برای هر سورس جدید هم یکی بسازی)
forwarder = MultiForwarder(source_chat="me")  # پیش‌فرض سورس: Saved Messages

# -------------------------------
# 📌 مدیریت پیام‌ها
# -------------------------------
async def add_fmsg(msg: Message, msg_id: int = None) -> str:
    """افزودن msg_id به لیست پیام‌ها"""
    if msg_id is None:
        if not msg.reply_to_message:
            return "❗ برای ثبت پیام، روی آن ریپلای کن یا msg_id بده."
        msg_id = msg.reply_to_message.id
    forwarder.add_message(msg_id)
    return f"✅ پیام {msg_id} به لیست اضافه شد."

async def clear_fmsgs() -> str:
    forwarder.clear_messages()
    return "🧹 لیست پیام‌ها پاک شد."

# -------------------------------
# 📌 مدیریت تارگت‌ها
# -------------------------------
async def add_ftarget(chat_id: int) -> str:
    forwarder.add_target(chat_id)
    return f"🎯 تارگت {chat_id} اضافه شد."

async def clear_ftargets() -> str:
    forwarder.clear_targets()
    return "🧹 لیست تارگت‌ها پاک شد."

# -------------------------------
# 📌 تنظیمات
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
