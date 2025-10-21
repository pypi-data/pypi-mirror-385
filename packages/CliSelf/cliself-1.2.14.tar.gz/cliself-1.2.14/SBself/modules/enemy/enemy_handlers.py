
# -*- coding: utf-8 -*-
# File: SBself/modules/enemy_handlers/handlers.py
#
# ماژول هندلرهای «دشمن» (معمولی + ویژه) و «بی‌صدا»
# فقط کافی‌ست در main.py این ماژول را رجیستر کنید:
#     from SBself.modules.enemy_handlers.handlers import register as register_enemy_handlers
#     register_enemy_handlers(app)
#
# این نسخه با ساختار جدید پروژه هماهنگ شده و از AllConfig و فیلترها و utils داخلی استفاده می‌کند.

from __future__ import annotations

import asyncio
import random
from pyrogram import Client
from pyrogram.types import Message

from ...config import AllConfig
from ...filters.SBfilters import enemy_filter, special_enemy_filter, mute_filter
from ...core.utils import out_text, maybe_typing

def _enemy_config() -> dict:
    # اطمینان از وجود دیکشنری‌های موردنیاز
    AllConfig.setdefault("enemy", {})
    AllConfig["enemy"].setdefault("enemy_counter", {})
    return AllConfig["enemy"]

def register(app: Client) -> None:
    """ثبت سه هندلر: enemy، special_enemy و mute."""

    @app.on_message(enemy_filter)
    async def handle_enemy(client: Client, message: Message):
        cfg = _enemy_config()
        uid = int(message.from_user.id) if message.from_user else None
        if uid is None:
            return

        N = int(cfg.get("enemy_ignore", 0))
        cnt = int(cfg.get("enemy_counter", {}).get(uid, N))

        if cnt >= N:
            # متن را از util آماده می‌کنیم (base + caption + mentions)
            txt = out_text()
            if txt is None:
                return
            # شبیه‌سازی تایپ اگر فعال باشد
            await maybe_typing(client, message.chat.id, 2)
            try:
                await message.reply(txt)
            finally:
                cfg["enemy_counter"][uid] = 0
        else:
            cfg["enemy_counter"][uid] = cnt + 1

    @app.on_message(mute_filter)
    async def handle_mute(client: Client, message: Message):
        # پاک کردن پیام‌های کاربرانی که در لیست mute هستند
        try:
            await message.delete()
        except Exception:
            # مطمئن نیستیم کلاینت/مجوز اجازه حذف بده؛ اشکالی ندارد.
            pass

    @app.on_message(special_enemy_filter)
    async def handle_special_enemy(client: Client, message: Message):
        cfg = _enemy_config()

        # تاخیر تصادفی براساس SPTimelist (اگر خالی بود: ۱ ثانیه)
        tlist = cfg.get("SPTimelist", []) or []
        try:
            t = int(random.choice(tlist)) if tlist else 1
        except Exception:
            t = 1
        await asyncio.sleep(max(0, t))

        texts = cfg.get("specialenemytext", []) or []
        if not texts:
            return

        # اگر typing_on فعال باشد، چند ثانیه تایپ کنیم
        await maybe_typing(client, message.chat.id, 2)

        # متن ویژه را پاسخ بدهیم
        try:
            await message.reply(random.choice(texts))
        except Exception:
            pass
