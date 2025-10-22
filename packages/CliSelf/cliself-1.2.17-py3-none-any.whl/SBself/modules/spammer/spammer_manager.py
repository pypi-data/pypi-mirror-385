# -*- coding: utf-8 -*-
# File: SBself/spammer/spammer_manager.py

import asyncio
from typing import Optional
from ...config import AllConfig
from .spammer import Spammer
from .spammer_on_message import start_kill , stop_kill

# نگهدارنده وضعیت اسپمر
_spammer_instance: Optional[Spammer] = None
_spammer_task: Optional[asyncio.Task] = None


async def start_spammer():
    """
    شروع اسپمر برای چت‌های مشخص‌شده
    """
    global _spammer_instance, _spammer_task

    if _spammer_instance and _spammer_instance.is_spamming:
        return "⚠️ اسپمر از قبل در حال اجرا است."

    # مقداردهی اولیه اسپمر
    _spammer_instance = Spammer()
    _spammer_instance.is_spamming = True
    AllConfig["spammer"]["run_spammer"] = True

    _spammer_task = asyncio.create_task(_spammer_instance.run())
    return f"✅ اسپمر با {len(_spammer_instance.chat_ids)} چت شروع شد."


async def stop_spammer():
    """
    توقف اسپمر
    """
    global _spammer_instance, _spammer_task

    if not _spammer_instance or not _spammer_instance.is_spamming:
        return "⚠️ اسپمر در حال اجرا نیست."

    _spammer_instance.stop()
    AllConfig["spammer"]["run_spammer"] = False

    if _spammer_task:
        _spammer_task.cancel()
        _spammer_task = None

    _spammer_instance = None
    return "🛑 اسپمر متوقف شد."


async def set_spam_time(seconds: int):
    """
    تنظیم زمان تاخیر اسپمر (ثانیه)
    """
    if seconds <= 0:
        return "❌ مقدار زمان معتبر نیست."
    AllConfig["spammer"]["time"] = seconds
    return f"⏱ زمان اسپمر روی {seconds} ثانیه تنظیم شد."


def get_spammer_status():
    """
    وضعیت فعلی اسپمر
    """
    if _spammer_instance and _spammer_instance.is_spamming:
        return {
            "status": "running",
            "chat_ids": _spammer_instance.chat_ids,
            "delay": AllConfig["spammer"]["time"],
        }
    return {"status": "stopped"}


def is_spammer_running() -> bool:
    """
    بررسی فعال بودن اسپمر
    """
    return bool(_spammer_instance and _spammer_instance.is_spamming)

def start_spam_on_message(client,chat_id,reply_id):
    start_kill(client,chat_id,reply_id)
    
def stop_spam_on_message():
    stop_kill()