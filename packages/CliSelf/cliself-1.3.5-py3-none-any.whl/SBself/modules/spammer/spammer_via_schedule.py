# -*- coding: utf-8 -*-
# File: SBself/spammer/spammer_via_schedule.py

import asyncio
import datetime
from pyrogram.raw import functions
from ...config import AllConfig 


# ==============================
# 🕒 زمان‌بندی پیام‌ها (Scheduler)
# ==============================

async def schedule_next_message(client, interval: int) -> None:
    """
    ارسال پیام زمان‌بندی‌شده بعد از فاصله زمانی مشخص
    """
    timer_cfg = AllConfig["timer"]
    chat_id = timer_cfg.get("chat_id")
    if not chat_id:
        return

    try: 
        scheduled_time = timer_cfg["first_time"] + datetime.timedelta(minutes=interval)

        await client.send_message(
            chat_id=chat_id,
            text=timer_cfg["text"],
            schedule_date=datetime.datetime.fromtimestamp(scheduled_time.timestamp()),
        )

        timer_cfg["last_interval"] = interval
        await asyncio.sleep(2)

    except Exception as e:
        print(f"[Scheduler] Error scheduling message: {e}")


# ==============================
# ▶️ شروع تایمر اسپمر
# ==============================

async def start_scheduler_spammer(client, chat_id: int = None) -> str:
    """
    شروع تایمر برای ارسال پیام‌ها به‌صورت زمان‌بندی‌شده
    """
    timer_cfg = AllConfig["timer"]

    if not timer_cfg.get("text"):
        return "❌ متن تایمر تنظیم نشده!"
    if timer_cfg.get("time", 0) <= 0:
        return "❌ فاصله تایمر تنظیم نشده!"
    
    chat_id = chat_id or timer_cfg.get("chat_id")
    if not chat_id:
        return "⚠️ شناسه چت مشخص نیست!"

    timer_cfg.update({
        "chat_id": chat_id,
        "first_time": datetime.datetime.now(),
        "last_interval": 0,
        "is_running": True,
    })

    repeat = int(timer_cfg.get("repeat", 1))
    interval = int(timer_cfg.get("time", 10))

    for i in range(repeat):
        if not timer_cfg["is_running"]:
            break
        await schedule_next_message(client, interval * (i + 1))

    return f"✅ تایمر برای {repeat} پیام با فاصله {interval} دقیقه شروع شد."


# ==============================
# ⏹ توقف تایمر اسپمر
# ==============================

async def stop_scheduler_spammer(app) -> str:
    """
    حذف تمام پیام‌های زمان‌بندی‌شده و توقف تایمر
    """
    timer_cfg = AllConfig["timer"]
    chat_id = timer_cfg.get("chat_id")

    if not chat_id:
        return "❌ تایمر فعال نیست!"

    try:
        peer = await app.resolve_peer(chat_id)
        scheduled = await app.invoke(
            functions.messages.GetScheduledHistory(peer=peer, hash=0)
        )
        if scheduled.messages:
            ids = [msg.id for msg in scheduled.messages]
            await app.invoke(functions.messages.DeleteScheduledMessages(peer=peer, id=ids))
    except Exception as e:
        return f"⚠️ خطا در توقف تایمر: {e}"
    finally:
        timer_cfg.update({
            "chat_id": None,
            "is_running": False,
            "first_time": None,
            "last_interval": 0,
        })
    return "✨ تایمر با موفقیت متوقف شد."


# ==============================
# ⚙️ ابزار کمکی برای تنظیمات تایمر
# ==============================

def set_timer_text(text: str) -> str:
    """تنظیم متن پیام تایمر"""
    AllConfig["timer"]["text"] = text.strip()
    return f"📝 متن تایمر تنظیم شد: {text.strip()[:30]}..."

def set_timer_interval(minutes: int) -> str:
    """تنظیم فاصله بین پیام‌ها"""
    if minutes <= 0:
        return "❌ عدد معتبر وارد کنید."
    AllConfig["timer"]["time"] = minutes
    return f"⏱ فاصله تایمر روی {minutes} دقیقه تنظیم شد."

def set_timer_repeat(count: int) -> str:
    """تنظیم تعداد تکرار پیام‌ها"""
    if count <= 0:
        return "❌ عدد معتبر وارد کنید."
    AllConfig["timer"]["repeat"] = count
    return f"🔁 تایمر برای {count} تکرار تنظیم شد."

def get_timer_status() -> str:
    """گزارش وضعیت فعلی تایمر"""
    cfg = AllConfig["timer"]
    if not cfg.get("is_running"):
        return "🕓 تایمر غیرفعال است."
    text = cfg["text"][:30] + ("..." if len(cfg["text"]) > 30 else "")
    return (
        "📊 وضعیت تایمر:\n"
        f"• فعال: ✅\n"
        f"• متن: {text}\n"
        f"• فاصله: {cfg['time']} دقیقه\n"
        f"• تکرار: {cfg['repeat']} بار\n"
        f"• آخرین فاصله: {cfg['last_interval']} دقیقه"
    )
