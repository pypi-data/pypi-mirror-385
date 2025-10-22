# -*- coding: utf-8 -*-
# File: SBself/modules/gp_id_commands.py
#
# دستورات:
#   /gp_id   → نمایش اطلاعات چت جاری
#   /user_id → نمایش اطلاعات کاربر/پیام (خروجی id_manager.get_id_info)
#
# رفتار: ابتدا تلاش می‌کند «پیام دستور» را ویرایش (edit) کند؛
# در صورت خطا (مثلاً چون outgoing نیست)، به‌جایش reply ارسال می‌شود.

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter
from SBself.core.gp_id_manager import fetch_group_info_text
from SBself.core.id_manager import get_id_info
from SBself.core.edit_and_reply import _edit_or_reply



def register(app: Client) -> None:
    @app.on_message(admin_filter & filters.command("gp_id", prefixes=["/", ""]))
    async def _gp_id(client: Client, m: Message):
        # متن را می‌گیریم، سپس edit-or-reply
        text = await fetch_group_info_text(client, m.chat.id)
        await _edit_or_reply(m, text, disable_web_page_preview=True)

    @app.on_message(admin_filter & filters.command("user_id", prefixes=["/", ""]))
    async def _user_id(client: Client, m: Message):
        # خروجی id_manager ممکن است شامل فرمت خاص باشد؛ فقط edit-or-reply می‌کنیم
        text = await get_id_info(client, m)
        await _edit_or_reply(m, text, disable_web_page_preview=True)
