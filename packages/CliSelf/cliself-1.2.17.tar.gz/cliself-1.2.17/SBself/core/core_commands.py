
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/core/core_commands.py
#
# رجیستر ماژولی دستورات سیستمی (ping / uptime / status / restart / shutdown / help)
# استفاده در main.py:
#   from SBself.core.core_commands import register as register_core_commands
#   register_core_commands(app)

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter
from SBself.core.core_cmds import ping, uptime, status, restart, shutdown, help_text

def register(app: Client) -> None:
    # --- ping ---
    @app.on_message(admin_filter & filters.command("ping", prefixes=["/", ""]))
    async def _ping(client: Client, m: Message):
        # پاس دادن client و chat_id برای پینگ واقعی
        await m.reply(await ping(client, m.chat.id if m.chat else None))

    # --- uptime ---
    @app.on_message(admin_filter & filters.command("uptime", prefixes=["/", ""]))
    async def _uptime(client: Client, m: Message):
        await m.reply(await uptime())

    # --- status ---
    @app.on_message(admin_filter & filters.command("status", prefixes=["/", ""]))
    async def _status(client: Client, m: Message):
        await m.reply(await status())

    # --- restart ---
    @app.on_message(admin_filter & filters.command("restart", prefixes=["/", ""]))
    async def _restart(client: Client, m: Message):
        await m.reply("♻️ Restarting...")
        await restart()

    # --- shutdown ---
    @app.on_message(admin_filter & filters.command("shutdown", prefixes=["/", ""]))
    async def _shutdown(client: Client, m: Message):
        await m.reply("🛑 Shutting down...")
        await shutdown()

    # --- help ---
    @app.on_message(admin_filter & filters.command(["help", "h"], prefixes=["/", ""]))
    async def _help(client: Client, m: Message):
        await m.reply(await help_text())

    # --- Aliases / shortcuts ---
    @app.on_message(admin_filter & filters.command(["alive"], prefixes=["/", ""]))
    async def _alive(client: Client, m: Message):
        p = await ping(client, m.chat.id if m.chat else None)
        u = await uptime()
        await m.reply(f"{p}\n{u}")
