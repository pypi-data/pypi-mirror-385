
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/core/core_cmds.py

import time, sys, os, statistics, asyncio
from datetime import timedelta
from typing import Optional
from pyrogram import Client
from ..config import AllConfig

START_TIME = time.time()

async def _probe_api_latency(client: Client, trials: int = 3) -> float:
    """Measure API round-trip (ms) via lightweight get_me() calls and return median."""
    results = []
    for _ in range(max(1, trials)):
        t0 = time.perf_counter()
        try:
            await client.get_me()
        except Exception:
            # Even if it fails, record a high value to reflect issues
            results.append(10_000.0)
        else:
            dt_ms = (time.perf_counter() - t0) * 1000.0
            results.append(dt_ms)
        await asyncio.sleep(0)  # yield
    return float(statistics.median(results)) if results else float('nan')

async def _probe_chat_action_latency(client: Client, chat_id: Optional[int]) -> Optional[float]:
    """Measure latency for a chat-bound action (typing) if chat_id provided."""
    if chat_id is None:
        return None
    t0 = time.perf_counter()
    try:
        await client.send_chat_action(chat_id, "typing")
    except Exception:
        return None
    return (time.perf_counter() - t0) * 1000.0

async def ping(client: Optional[Client] = None, chat_id: Optional[int] = None) -> str:
    """پینگ واقعی: اندازه‌گیری تاخیر API و در صورت امکان تاخیر ارسال اکشن به چت."""
    # If no client provided, fall back to simple pong
    if client is None:
        return "PING"
    api_ms = await _probe_api_latency(client, trials=3)
    chat_ms = await _probe_chat_action_latency(client, chat_id)
    parts = [ "PING" ]
    if api_ms == api_ms:  # not NaN
        parts.append(f"• API: {api_ms:.0f} ms (median)")
    if chat_ms is not None:
        parts.append(f"• ChatAction: {chat_ms:.0f} ms")
    return "\n".join(parts)

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
        "- ping → تست اتصال + پینگ واقعی\n"
        "- uptime → نمایش زمان اجرا\n"
        "- restart → ریستارت برنامه\n"
        "- shutdown → خاموش کردن\n"
        "- status → وضعیت برنامه\n"
        "- help → نمایش همین راهنما\n"
    )
