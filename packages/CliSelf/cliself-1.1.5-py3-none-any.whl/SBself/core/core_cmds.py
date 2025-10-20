# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/core_cmds.py

import time, sys, os
from datetime import timedelta
from ..config import AllConfig

START_TIME = time.time()


async def ping() -> str:
    """نمایش وضعیت زنده بودن"""
    return "pong 🏓"


async def uptime() -> str:
    """نمایش مدت زمان اجرای برنامه"""
    now = time.time()
    delta = timedelta(seconds=int(now - START_TIME))
    return f"⏱ Uptime: {delta}"


async def restart() -> str:
    """راه‌اندازی مجدد پروسه"""
    os.execl(sys.executable, sys.executable, *sys.argv)
    return "♻️ Restarting..."


async def shutdown() -> str:
    """خاموش کردن پروسه"""
    os._exit(0)
    return "🛑 Shutting down..."


async def status() -> str:
    """نمایش وضعیت کلی (ادمین‌ها، زمان، تنظیمات مهم)"""
    admins = AllConfig.get("admins", [])
    run_kill = AllConfig.get("run_kill", False)
    typing_on = AllConfig.get("typing_on", False)

    return (
        "📊 وضعیت فعلی:\n"
        f"- تعداد ادمین‌ها: {len(admins)}\n"
        f"- kill: {'در حال اجرا' if run_kill else 'متوقف'}\n"
        f"- typing: {'فعال' if typing_on else 'غیرفعال'}\n"
    )


async def help_text() -> str:
    """برگرداندن متن راهنما"""
    return (
        "📖 راهنمای دستورات:\n"
        "- ping → تست اتصال\n"
        "- uptime → نمایش زمان اجرا\n"
        "- restart → ریستارت برنامه\n"
        "- shutdown → خاموش کردن\n"
        "- status → وضعیت برنامه\n"
        "- help → نمایش همین راهنما\n"
    )
