# -*- coding: utf-8 -*-
# File: SBself/core/off_manager.py

from __future__ import annotations
import asyncio
import os
from typing import Optional
from pyrogram import Client, filters

# فیلتر ادمین پروژه
from SBself.filters.SBfilters import admin_filter


async def graceful_shutdown(client: Client, exit_code: int = 0, delay_sec: float = 0.2) -> None:
    """خاموشی نرم: مکث کوتاه، توقف کلاینت، خروج از پروسه."""
    try:
        if delay_sec > 0:
            await asyncio.sleep(delay_sec)
    except Exception:
        pass

    try:
        await client.stop()
    except Exception:
        pass

    try:
        raise SystemExit(exit_code)
    except SystemExit:
        os._exit(exit_code)


def register_off_commands(app: Client) -> None:
    """ثبت فرمان /off off"""

    @app.on_message(admin_filter & filters.command(["off"], prefixes=["/", ""]))
    async def _off_cmd(client: Client, m):
        if len(m.command) < 2 or m.command[1].lower() != "off":
            return await m.reply("Usage: /off off")
        await m.reply("🛑 برنامه خاموش شد.")
        await graceful_shutdown(client)


__all__ = ["graceful_shutdown", "register_off_commands"]
