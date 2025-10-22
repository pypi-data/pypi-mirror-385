# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer_manager.py
#
# مدیر اسپمر — هماهنگ با نسخه‌ی Threading در spammer.py
# - این ماژول خودش async نیست؛ اسپمر Thread-محور است.
# - توابع start/stop اینجا async هستند تا با هندلرهای Pyrogram سازگار بمانند.
# - هیچ تغییری در kill/on_message و زمان‌بندی ایجاد نمی‌کند.

from __future__ import annotations

import asyncio
from typing import Optional, List

from ...config import AllConfig
from .spammer import Spammer
from .spammer_on_message import start_kill, stop_kill

try:
    from ...core.logger import get_logger
    logger = get_logger("spammer_manager")
except Exception:
    import logging
    logger = logging.getLogger("spammer_manager")


# وضعیت سراسری اسپمرِ Threading
_spammer_instance: Optional[Spammer] = None
_spammer_client: Optional[object] = None  # همان client که به send_message دسترسی دارد


def _ensure_spammer_config():
    """اطمینان از وجود کلیدهای لازم در کانفیگ."""
    scfg = AllConfig.setdefault("spammer", {})
    scfg.setdefault("targets", [])
    scfg.setdefault("time", 10)
    scfg.setdefault("run_spammer", False)
    scfg.setdefault("typing_on", False)


def _is_running() -> bool:
    return bool(_spammer_instance and _spammer_instance.is_running())


async def start_spammer(client, chat_ids: Optional[List[int]] = None):
    """
    شروع اسپمر Threading برای چت‌های مشخص‌شده.
    - client: کلاینتی که متدهای sync مثل send_message / send_chat_action را فراهم می‌کند
              (یا از آداپتر همگام استفاده کرده‌اید).
    - chat_ids: در صورت ارسال، به عنوان تارگت‌های جدید ست می‌شود.
    """
    global _spammer_instance, _spammer_client

    _ensure_spammer_config()

    if _is_running():
        return {"status": "already_running", "targets": list(AllConfig["spammer"]["targets"])}

    if chat_ids is not None:
        AllConfig["spammer"]["targets"] = list(chat_ids)

    # ایجاد و استارت اسپمر Threading
    _spammer_instance = Spammer()
    _spammer_client = client
    try:
        _spammer_instance.start(_spammer_client)
    except Exception as e:
        _spammer_instance = None
        _spammer_client = None
        logger.error(f"Failed to start spammer: {e}")
        return {"status": "error", "error": str(e)}

    AllConfig["spammer"]["run_spammer"] = True
    logger.info(f"Spammer started with {len(AllConfig['spammer']['targets'])} targets.")
    return {
        "status": "started",
        "targets": list(AllConfig["spammer"]["targets"]),
        "delay": int(AllConfig["spammer"]["time"]),
    }


async def stop_spammer():
    """
    توقف تمیز اسپمر Threading.
    """
    global _spammer_instance, _spammer_client

    if not _is_running():
        return {"status": "not_running"}

    try:
        _spammer_instance.stop()
    except Exception as e:
        logger.warning(f"Error while stopping spammer: {e}")

    AllConfig["spammer"]["run_spammer"] = False
    _spammer_instance = None
    _spammer_client = None

    logger.info("Spammer stopped.")
    return {"status": "stopped"}


async def set_spam_time(seconds: int):
    """
    تنظیم زمان تاخیر اسپمر (ثانیه). در صورت درحال اجرا بودن، بلافاصله اعمال می‌شود.
    """
    _ensure_spammer_config()

    if seconds <= 0:
        return "❌ مقدار زمان معتبر نیست."

    AllConfig["spammer"]["time"] = int(seconds)

    if _is_running():
        try:
            _spammer_instance.set_delay(int(seconds))
        except Exception:
            pass

    return f"⏱ زمان اسپمر روی {int(seconds)} ثانیه تنظیم شد."


def get_spammer_status():
    """
    وضعیت فعلی اسپمر.
    """
    _ensure_spammer_config()
    if _is_running():
        return {
            "status": "running",
            "targets": list(AllConfig["spammer"]["targets"]),
            "delay": int(AllConfig["spammer"]["time"]),
        }
    return {"status": "stopped"}


def is_spammer_running() -> bool:
    """
    بررسی فعال بودن اسپمر (Threading).
    """
    return _is_running()


# -----------------------------
# رله‌های on_message (بدون تغییر در منطق kill)
# -----------------------------
async def start_spam_on_message(client, chat_id: int, reply_id: int):
    """
    راه‌اندازی حلقه‌ی kill برای یک پیام مشخص (reply) — همان منطق فعلی.
    """
    return await start_kill(client, chat_id, reply_id)

async def stop_spam_on_message():
    """
    توقف حلقه‌ی kill — همان منطق فعلی.
    """
    return await stop_kill()
