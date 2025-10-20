# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_cmds.py

from typing import Union, Optional
from pyrogram.types import Message
from .multi_forward_manager import MultiForwarder

forwarder = MultiForwarder()

# -------------------------------
# 📌 افزودن پیام (فقط فوروارد؛ کانال/گروه/پیوی)
# -------------------------------
async def add_fmsg(msg: Message, _unused: Optional[int] = None) -> str:
    """
    سناریوهای پشتیبانی‌شده:
      1) ریپلای روی پیام فورواردی از کانال/گروه:
         - اگر forward_from_chat و forward_from_message_id وجود داشت → همان منبع/آی‌دی فوروارد می‌شود.
      2) ریپلای روی خود پیام در گروه/سوپرگروه:
         - از chat.id همان گروه و message.id همان پیام استفاده می‌شود.
      3) ریپلای روی خود پیام در پیویِ شخص:
         - از chat.id همان پیوی و message.id همان پیام استفاده می‌شود (هدِر «Forwarded from <name>»).
      ⚠️ ریپلای در Saved Messages (me) پذیرفته نمی‌شود تا منبع «فرد» باقی بماند.
    """
    if not msg.reply_to_message:
        return "❗ برای ثبت پیام، روی خود پیام ریپلای کن (در پیوی شخص/گروه/یا پیام فورواردی)."

    src = msg.reply_to_message

    # 1) پیام فورواردی از کانال/گروه (دارای منبع واقعی)
    fchat = getattr(src, "forward_from_chat", None)
    fmsg_id = getattr(src, "forward_from_message_id", None)
    if fchat and fmsg_id:
        forward_chat_id: Union[int, str] = getattr(fchat, "id", None) or getattr(fchat, "username", None)
        if forward_chat_id is None:
            return "❌ شناسه‌ی منبع فوروارد در دسترس نیست."
        forwarder.add_item(forward_chat_id=forward_chat_id, forward_message_id=int(fmsg_id))
        return f"✅ پیام فورواردی ثبت شد → from={forward_chat_id}, mid={fmsg_id}"

    # 2) جلوگیری از ثبت پیام داخل Saved Messages (me)
    #    چون در این حالت منبع «Saved Messages» می‌شود و نام شخص نمایش داده نمی‌شود.
    chat_obj = src.chat
    # pyrogram: chat_obj.is_self فقط در Saved Messages True است
    if getattr(chat_obj, "is_self", False):
        return "❌ روی پیام داخل Saved Messages ریپلای نکن. لطفاً داخل **پیوی همان شخص** روی پیامش ریپلای کن تا منبع «از چه فردی» درست نمایش داده شود."

    # 3) پیام داخل گروه/سوپرگروه یا پیوی کاربر (غیرفوروارد)
    #    از همان چت و همان msg.id فوروارد می‌کنیم؛ هدر «Forwarded from ...» طبق سازوکار تلگرام نمایش داده می‌شود.
    src_chat_id = chat_obj.id
    src_msg_id = src.id
    forwarder.add_item(forward_chat_id=src_chat_id, forward_message_id=src_msg_id)
    return f"✅ پیام از چت جاری ثبت شد → chat={src_chat_id}, mid={src_msg_id}"

# -------------------------------
# بقیهٔ توابع بدون تغییر
# -------------------------------
async def clear_fmsgs() -> str:
    forwarder.clear_items()
    return "🧹 لیست پیام‌ها پاک شد."

async def add_ftarget(chat_id: Union[int, str]) -> str:
    forwarder.add_target(chat_id)
    return f"🎯 تارگت `{chat_id}` اضافه شد."

async def clear_ftargets() -> str:
    forwarder.clear_targets()
    return "🧹 لیست تارگت‌ها پاک شد."

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

async def start_forward(client) -> str:
    return await forwarder.start(client)

async def stop_forward() -> str:
    return await forwarder.stop()

async def forward_status() -> str:
    return forwarder.status()
