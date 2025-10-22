# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer_commands.py
#
# دستورات اسپمر و تایمر + مدیریت تارگت‌ها
#  - SPAMMER: /time  /kill  /stop_kill  /start_spammer  /stop_spammer
#  - TIMER: /start_timer  /stop_timer  /timer_status  /timer_text  /timer_interval  /timer_repeat
#  - TARGETS:
#       * اسپمر:  /spam_addtarget  /spam_deltarget  /spam_cleartargets  /spam_targets
#       * تایمر:  /timer_addtarget /timer_deltarget /timer_cleartargets /timer_targets
#
# استفاده در main.py:
#   from SBself.modules.spammer.spammer_commands import register as register_spammer_commands
#   register_spammer_commands(app)

from __future__ import annotations

import re
from typing import Optional, List

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied

from SBself.filters.SBfilters import admin_filter
from SBself.config import AllConfig

from .spammer_manager import (
    start_spammer,          # async start_spammer(client, chat_ids=None)
    stop_spammer,           # async
    set_spam_time,          # async
    start_spam_on_message,  # async
    stop_spam_on_message,   # async
    is_spammer_running,     # sync
)
from .spammer_via_schedule import (
    start_scheduler_spammer,  # async
    stop_scheduler_spammer,   # async
    get_timer_status,         # sync (بر اساس نسخه فعلی شما)
    set_timer_text,           # sync
    set_timer_interval,       # sync
    set_timer_repeat,         # sync
)
from .auto_timer_handler import handle_auto_timer


# =========================================================
# Helpers
# =========================================================

async def _resolve_id_token(client: Client, token: Optional[str], fallback_chat_id: Optional[int] = None) -> Optional[int]:
    """
    token: "me" | عدد | @username | t.me/username | None
    اگر None/خالی باشد، از fallback_chat_id استفاده می‌کند.
    """
    if token is None or token.strip() == "":
        return fallback_chat_id

    t = token.strip()
    if t.lower() == "me":
        me = await client.get_me()
        return int(me.id)

    # chat_id عددی
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except Exception:
            return None

    # username
    username = t
    if username.startswith("@"):
        username = username[1:]
    if "t.me/" in username.lower():
        username = re.sub(r"^https?://t\.me/", "", username, flags=re.IGNORECASE).strip("/")

    try:
        ch = await client.get_chat(username)
        return int(ch.id)
    except (UsernameNotOccupied, Exception):
        return None


def _get_spammer_targets() -> List[int]:
    """لیست تارگت‌های اسپمر از AllConfig."""
    spammer = AllConfig.setdefault("spammer", {})
    return spammer.setdefault("targets", [])


def _get_timer_targets() -> List[int]:
    """لیست تارگت‌های تایمر از AllConfig."""
    timer = AllConfig.setdefault("timer", {})
    return timer.setdefault("targets", [])


def _add_id_to_list(lst: List[int], cid: int) -> bool:
    cid = int(cid)
    if cid not in lst:
        lst.append(cid)
        return True
    return False


def _del_id_from_list(lst: List[int], cid: int) -> bool:
    cid = int(cid)
    try:
        lst.remove(cid)
        return True
    except ValueError:
        return False


def _format_targets(lst: List[int]) -> str:
    if not lst:
        return "هیچ تارگتی ثبت نشده."
    return "\n".join(f"- `{i}`" for i in lst)


# =========================================================
# Register all handlers
# =========================================================

def register(app: Client) -> None:
    # -----------------------------
    # 🔥 SPAMMER
    # -----------------------------
    @app.on_message(admin_filter & filters.command("time", prefixes=["/", ""]))
    async def _time(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /time <seconds>")
        try:
            sec = int(m.command[1])
        except Exception:
            return await m.reply("❌ مقدار زمان نامعتبر است.")
        msg = await set_spam_time(sec)
        await m.reply(msg)

    @app.on_message(admin_filter & filters.command("kill", prefixes=["/", ""]) & filters.reply)
    async def _kill(client: Client, m: Message):
        # شروع اسپم روی پیام ریپلای‌شده (حالت kill)
        await start_spam_on_message(client, m.chat.id, m.reply_to_message.id)

    @app.on_message(admin_filter & filters.command("stop_kill", prefixes=["/", ""]))
    async def _stop_kill(client: Client, m: Message):
        await stop_spam_on_message()
        await m.reply("🛑 حالت kill متوقف شد.")

    @app.on_message(admin_filter & filters.command("start_spammer", prefixes=["/", ""]))
    async def _start_spam(client: Client, m: Message):
        """
        شروع اسپمر Threading:
        - اگر آرگومان‌ها داده شده باشند (ids بعد از دستور)، همان‌ها تارگت می‌شوند.
        - در غیراینصورت، از لیست ذخیره‌شده استفاده می‌کند؛ اگر خالی بود، همین چت جاری را تارگت می‌کند.
        """
        target_ids: List[int] = []
        # از آرگومان‌ها استخراج کنیم (اختیاری)
        if m.command and len(m.command) > 1:
            raw_ids = m.command[1:]
            for tok in raw_ids:
                cid = await _resolve_id_token(client, tok)
                if cid is not None:
                    target_ids.append(cid)

        # اگر هیچ آرگومانی نبود، از لیست ذخیره‌شده یا چت جاری
        if not target_ids:
            saved = list(_get_spammer_targets())
            target_ids = saved if saved else [m.chat.id]

        res = await start_spammer(client, chat_ids=target_ids)
        # وضعیت را برای کاربر بازتاب بدهیم
        if res.get("status") == "started":
            await m.reply(f"🚀 اسپمر شروع شد.\n🎯 Targets: {', '.join(map(str, res.get('targets', [])))}\n⏱ Delay: {res.get('delay', '?')}s")
        elif res.get("status") == "already_running":
            await m.reply("⚠️ اسپمر از قبل در حال اجراست.")
        elif res.get("status") == "error":
            await m.reply(f"❌ خطا در شروع اسپمر: {res.get('error')}")
        else:
            await m.reply(f"ℹ️ نتیجه: {res}")

    @app.on_message(admin_filter & filters.command("stop_spammer", prefixes=["/", ""]))
    async def _stop_spam(client: Client, m: Message):
        res = await stop_spammer()
        if res.get("status") == "stopped":
            await m.reply("🛑 اسپمر متوقف شد.")
        elif res.get("status") == "not_running":
            await m.reply("ℹ️ اسپمر در حال اجرا نیست.")
        else:
            await m.reply(f"ℹ️ نتیجه: {res}")

    # -----------------------------
    # 🎯 SPAMMER TARGETS
    # -----------------------------
    @app.on_message(admin_filter & filters.command("spam_addtarget", prefixes=["/", ""]))
    async def _spam_addtarget(client: Client, m: Message):
        tok = m.text.split(None, 1)[1].strip() if (m.text and len(m.command) > 1) else ""
        cid = await _resolve_id_token(client, tok, fallback_chat_id=m.chat.id)
        if cid is None:
            return await m.reply("❌ chat_id نامعتبر است.")
        lst = _get_spammer_targets()
        added = _add_id_to_list(lst, cid)
        return await m.reply("✅ تارگت اضافه شد." if added else "ℹ️ این تارگت از قبل وجود داشت.")

    @app.on_message(admin_filter & filters.command("spam_deltarget", prefixes=["/", ""]))
    async def _spam_deltarget(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /spam_deltarget <chat_id|@username|me>")
        cid = await _resolve_id_token(client, m.command[1])
        if cid is None:
            return await m.reply("❌ chat_id نامعتبر است.")
        lst = _get_spammer_targets()
        removed = _del_id_from_list(lst, cid)
        return await m.reply("🗑 تارگت حذف شد." if removed else "ℹ️ چنین تارگتی در لیست نبود.")

    @app.on_message(admin_filter & filters.command("spam_cleartargets", prefixes=["/", ""]))
    async def _spam_cleartargets(client: Client, m: Message):
        lst = _get_spammer_targets()
        lst.clear()
        return await m.reply("🧹 همهٔ تارگت‌های اسپمر پاک شد.")

    @app.on_message(admin_filter & filters.command("spam_targets", prefixes=["/", ""]))
    async def _spam_targets(client: Client, m: Message):
        lst = _get_spammer_targets()
        return await m.reply(_format_targets(lst))

    # -----------------------------
    # ⏱ TIMER (SCHEDULE SPAMMER)
    # -----------------------------
    @app.on_message(admin_filter & filters.command("start_timer", prefixes=["/", ""]))
    async def _timer_start(client: Client, m: Message):
        """
        استارت تایمر برای تمام تارگت‌های بخش تایمر؛ اگر لیست خالی بود، چت جاری را تارگت می‌کند.
        """
        targets = list(_get_timer_targets()) or [m.chat.id]
        ok = 0
        for t in targets:
            try:
                msg = await start_scheduler_spammer(client, t)
                # اگر پیام خاصی از تابع برگشت، می‌توان آن را بررسی کرد؛ فعلاً موفقیت را با رسیدن پاسخ بدون خطا می‌گیریم
                ok += 1 if (msg is None or "start" in str(msg).lower()) else 0
            except Exception:
                pass
        return await m.reply(f"⏱ تایمر برای {ok}/{len(targets)} تارگت فعال شد.")

    @app.on_message(admin_filter & filters.command("stop_timer", prefixes=["/", ""]))
    async def _timer_stop(client: Client, m: Message):
        try:
            msg = await stop_scheduler_spammer(client)
        except Exception:
            msg = "⏹ تایمر متوقف شد."
        await m.reply(msg)

    @app.on_message(admin_filter & filters.command("timer_status", prefixes=["/", ""]))
    async def _timer_status(client: Client, m: Message):
        await m.reply(get_timer_status())

    # Auto scheduler loop trigger on own messages
    @app.on_message(filters.text & filters.me)
    async def _auto_timer(client: Client, message: Message):
        await handle_auto_timer(client, message)

    # تنظیمات تایمر
    @app.on_message(admin_filter & filters.command("timer_text", prefixes=["/", ""]))
    async def _timer_text(client: Client, m: Message):
        text = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(set_timer_text(text))

    @app.on_message(admin_filter & filters.command("timer_interval", prefixes=["/", ""]))
    async def _timer_interval(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /timer_interval <minutes>")
        try:
            minutes = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر نیست.")
        await m.reply(set_timer_interval(minutes))

    @app.on_message(admin_filter & filters.command("timer_repeat", prefixes=["/", ""]))
    async def _timer_repeat(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /timer_repeat <count>")
        try:
            count = int(m.command[1])
        except Exception:
            return await m.reply("❌ عدد معتبر نیست.")
        await m.reply(set_timer_repeat(count))

    # -----------------------------
    # 🎯 TIMER TARGETS
    # -----------------------------
    @app.on_message(admin_filter & filters.command("timer_addtarget", prefixes=["/", ""]))
    async def _timer_addtarget(client: Client, m: Message):
        tok = m.text.split(None, 1)[1].strip() if (m.text and len(m.command) > 1) else ""
        cid = await _resolve_id_token(client, tok, fallback_chat_id=m.chat.id)
        if cid is None:
            return await m.reply("❌ chat_id نامعتبر است.")
        lst = _get_timer_targets()
        added = _add_id_to_list(lst, cid)
        return await m.reply("✅ تارگت اضافه شد." if added else "ℹ️ این تارگت از قبل وجود داشت.")

    @app.on_message(admin_filter & filters.command("timer_deltarget", prefixes=["/", ""]))
    async def _timer_deltarget(client: Client, m: Message):
        if not (m.text and len(m.command) > 1):
            return await m.reply("Usage: /timer_deltarget <chat_id|@username|me>")
        cid = await _resolve_id_token(client, m.command[1])
        if cid is None:
            return await m.reply("❌ chat_id نامعتبر است.")
        lst = _get_timer_targets()
        removed = _del_id_from_list(lst, cid)
        return await m.reply("🗑 تارگت حذف شد." if removed else "ℹ️ چنین تارگتی در لیست نبود.")

    @app.on_message(admin_filter & filters.command("timer_cleartargets", prefixes=["/", ""]))
    async def _timer_cleartargets(client: Client, m: Message):
        lst = _get_timer_targets()
        lst.clear()
        return await m.reply("🧹 همهٔ تارگت‌های تایمر پاک شد.")

    @app.on_message(admin_filter & filters.command("timer_targets", prefixes=["/", ""]))
    async def _timer_targets(client: Client, m: Message):
        lst = _get_timer_targets()
        return await m.reply(_format_targets(lst))
