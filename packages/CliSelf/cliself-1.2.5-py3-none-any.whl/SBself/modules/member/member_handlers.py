# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/member_handlers.py

from ...config import AllConfig


async def handle_user_join(client, message):
    """خوش‌آمدگویی به کاربر جدید"""
    join_text = AllConfig.get("join_text", "خوش آمدید 🌹")
    try:
        await message.reply(join_text)
    except Exception:
        pass


async def handle_user_left(client, message):
    """خداحافظی از کاربر خارج‌شده"""
    left_text = AllConfig.get("left_text", "خدانگهدار 👋")
    try:
        await message.reply(left_text)
    except Exception:
        pass
