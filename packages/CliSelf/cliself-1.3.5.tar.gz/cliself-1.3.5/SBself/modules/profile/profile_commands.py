
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/profile/profile_commands.py
#
# رجیستر دستورات پروفایل + مدیریت خودکار نام‌ها (Name Manager)
# استفاده در main.py:
#   from SBself.moudels.profile.profile_commands import register as register_profile_commands
#   register_profile_commands(app)

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter
from SBself.config import AllConfig

# بیزنس‌لاجیک پروفایل (بر اساس مسیر داده‌شده)
from SBself.modules.profile.profile_manager import (
    update_name, update_bio, update_username,
    update_photo, clear_photo, show_profile_status,
)

# نام‌گردان خودکار — ماژول هسته‌ای شما (طبق کد ارسالی در modules/name_manager.py)
from SBself.core.name_manager import (
    init_name_manager, nm_set_names, nm_set_interval, nm_toggle, nm_status
)

# اطمینان از وجود ساختار names در کانفیگ
names_cfg = AllConfig.setdefault("names", {})
names_cfg.setdefault("names", [])
names_cfg.setdefault("change_interval_h", 1)
names_cfg.setdefault("changenames", False)
names_cfg.setdefault("changenames_idx", 0)
names_cfg.setdefault("changenames_task", None)

def register(app: Client) -> None:
    # ---------- اتصال کلاینت به نام‌گردان در زمان رجیستر ----------
    try:
        init_name_manager(app)
    except Exception:
        # اگر ماژول موجود بود ولی init فراخوانی شکست خورد، از کار نمی‌افتیم
        pass

    # =============================
    # 🧍‍♂️ PROFILE COMMANDS
    # =============================
    @app.on_message(admin_filter & filters.command("setname", prefixes=["/", ""]))
    async def _set_name(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await update_name(client, txt))

    @app.on_message(admin_filter & filters.command("setbio", prefixes=["/", ""]))
    async def _set_bio(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await update_bio(client, txt))

    @app.on_message(admin_filter & filters.command("setusername", prefixes=["/", ""]))
    async def _set_username(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await update_username(client, txt))

    @app.on_message(admin_filter & filters.command("setphoto", prefixes=["/", ""]))
    async def _set_photo(client: Client, m: Message):
        await m.reply(await update_photo(client, m))

    @app.on_message(admin_filter & filters.command("delphoto", prefixes=["/", ""]))
    async def _del_photo(client: Client, m: Message):
        await m.reply(await clear_photo(client))

    @app.on_message(admin_filter & filters.command("profilestatus", prefixes=["/", ""]))
    async def _profile_status(client: Client, m: Message):
        await m.reply(await show_profile_status(client))

    # =============================
    # 🪄 AUTO NAME (NAME MANAGER)
    # =============================
    @app.on_message(admin_filter & filters.command("setnames", prefixes=["/", ""]))
    async def _setnames(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await nm_set_names(txt))

    @app.on_message(admin_filter & filters.command("name_interval", prefixes=["/", ""]))
    async def _name_interval(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: name_interval <hours>")
        try:
            hours = int(m.command[1])
        except Exception:
            return await m.reply("❌ مقدار معتبر نیست. مثال: /name_interval 2")
        await m.reply(await nm_set_interval(hours))

    @app.on_message(admin_filter & filters.command("name_toggle", prefixes=["/", ""]))
    async def _name_toggle(client: Client, m: Message):
        if not (m.text and len(m.command) > 1 and m.command[1].lower() in ["on", "off"]):
            return await m.reply("Usage: name_toggle <on|off>")
        enable = m.command[1].lower() == "on"
        await m.reply(await nm_toggle(enable))

    @app.on_message(admin_filter & filters.command("name_status", prefixes=["/", ""]))
    async def _name_status(client: Client, m: Message):
        await m.reply(await nm_status())
