
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/enemy/enemy_commands.py
#
# پکیج یکپارچه‌ی فرمان‌ها برای مدیریت Enemy (معمولی)، Special و Mute
# این فایل «هر دو» مجموعه دستورات قبلی را ادغام می‌کند و چند دستور کاربردی هم اضافه می‌کند.
#
# رجیستر در main.py:
#   from SBself.moudels.enemy.enemy_commands import register as register_enemy_commands
#   register_enemy_commands(app)

from __future__ import annotations

import re
from typing import Tuple, Optional, List, Dict
from pyrogram import Client, filters
from pyrogram.types import Message

# فیلتر ادمین و سایر فیلترهای پروژه
from SBself.filters.SBfilters import admin_filter
# کانفیگ کلی پروژه
from SBself.config import AllConfig

# ========================= Helpers & Config ===================================

def _cfg() -> dict:
    """برگشت/ایجاد ساختار کانفیگ دشمن‌ها"""
    AllConfig.setdefault("enemy", {})
    e = AllConfig["enemy"]
    e.setdefault("enemy_ignore", 0)          # چند پیام را نادیده بگیر قبل از پاسخ
    e.setdefault("enemy_counter", {})        # شمارنده هر یوزر
    e.setdefault("enemy_enabled", True)      # فعال/غیرفعال بودن enemy معمولی
    e.setdefault("enemy_users", {})          # uid->name دشمن‌های معمولی
    e.setdefault("special_users", {})        # uid->name دشمن‌های ویژه
    e.setdefault("specialenemytext", [])     # لیست متن‌های ویژه
    e.setdefault("SPTimelist", [])           # لیست تاخیرهای ویژه (ثانیه)
    e.setdefault("mute", [])                 # لیست uidهایی که میوت‌اند
    return e

async def _resolve_uid_and_name(client: Client, m: Message) -> Tuple[Optional[int], Optional[str]]:
    """استخراج uid و name از ریپلای/آرگومان/یوزرنیم"""
    # 1) ریپلای
    if m.reply_to_message and m.reply_to_message.from_user:
        u = m.reply_to_message.from_user
        return int(u.id), (u.first_name or "")
    # 2) آرگومان
    text = (m.text or "").strip()
    parts = text.split(maxsplit=1)
    arg = parts[1] if len(parts) > 1 else ""
    if arg.startswith("@"):
        try:
            user = await client.get_users(arg)
            return int(user.id), (user.first_name or "")
        except Exception:
            return None, None
    # 3) uid عددی
    try:
        if arg:
            uid = int(arg)
            name = ""
            try:
                user = await client.get_users(uid)
                name = (user.first_name or "")
            except Exception:
                pass
            return uid, name
    except Exception:
        pass
    return None, None

# ========================= Low-level ops (state) ==============================

async def add_enemy(uid: int, name: str) -> str:
    e = _cfg()
    e["enemy_users"][int(uid)] = name or ""
    return f"✅ دشمن اضافه شد: {uid} {name}".strip()

async def del_enemy(uid: int, name: str) -> str:
    e = _cfg()
    if int(uid) in e["enemy_users"]:
        e["enemy_users"].pop(int(uid), None)
        return f"✅ دشمن حذف شد: {uid} {name}".strip()
    return "ℹ️ این کاربر در لیست دشمن نبود."

async def clean_enemy() -> str:
    e = _cfg()
    e["enemy_users"] = {}
    return "🧹 لیست دشمن معمولی پاک شد."

async def list_enemy() -> str:
    e = _cfg()
    d: Dict[int, str] = e.get("enemy_users", {})
    if not d:
        return "لیست دشمن معمولی خالی است."
    body = "\n".join(f"{uid} — {name}" for uid, name in d.items())
    return "Enemy list:\n" + body

async def set_enemy_ignore(value: int) -> str:
    e = _cfg()
    e["enemy_ignore"] = max(0, int(value))
    return f"✅ enemy_ignore = {e['enemy_ignore']}"

async def add_special(uid: int, name: str) -> str:
    e = _cfg()
    e["special_users"][int(uid)] = name or ""
    return f"✅ دشمن ویژه اضافه شد: {uid} {name}".strip()

async def del_special(uid: int, name: str) -> str:
    e = _cfg()
    if int(uid) in e["special_users"]:
        e["special_users"].pop(int(uid), None)
        return f"✅ دشمن ویژه حذف شد: {uid} {name}".strip()
    return "ℹ️ این کاربر در لیست دشمن ویژه نبود."

async def clean_special() -> str:
    e = _cfg()
    e["special_users"] = {}
    return "🧹 لیست دشمن ویژه پاک شد."

async def list_special() -> str:
    e = _cfg()
    d: Dict[int, str] = e.get("special_users", {})
    if not d:
        return "لیست دشمن ویژه خالی است."
    body = "\n".join(f"{uid} — {name}" for uid, name in d.items())
    return "Special list:\n" + body

async def add_special_text(txt: str) -> str:
    e = _cfg()
    txt = (txt or "").strip()
    if not txt:
        return "❌ متن خالی است."
    e["specialenemytext"].append(txt)
    return "✅ یک متن ویژه اضافه شد."

async def remove_special_text(txt: str) -> str:
    e = _cfg()
    txt = (txt or "").strip()
    if not txt:
        return "❌ متن خالی است."
    try:
        e["specialenemytext"].remove(txt)
        return "✅ متن ویژه حذف شد."
    except ValueError:
        return "ℹ️ چنین متنی در لیست نبود."

async def clean_special_text() -> str:
    e = _cfg()
    e["specialenemytext"] = []
    return "🧹 تمام متن‌های ویژه پاک شد."

async def list_special_text() -> str:
    e = _cfg()
    arr = e.get("specialenemytext", [])
    if not arr:
        return "specialenemytext خالی است."
    body = "\n".join(f"[{i}] {t}" for i, t in enumerate(arr))
    return body

async def set_special_times(nums: List[int]) -> str:
    e = _cfg()
    arr = [max(0, int(x)) for x in nums if isinstance(x, int)]
    e["SPTimelist"] = arr
    return f"✅ SPTimelist = {arr}"

async def list_special_times() -> str:
    e = _cfg()
    arr = e.get("SPTimelist", [])
    if not arr:
        return "SPTimelist خالی است."
    return "\n".join(f"[{i}] {t}s" for i, t in enumerate(arr))

async def mute_user(uid: int, name: str) -> str:
    e = _cfg()
    if int(uid) not in e["mute"]:
        e["mute"].append(int(uid))
    return f"🔇 کاربر میوت شد: {uid} {name}".strip()

async def unmute_user(uid: int, name: str) -> str:
    e = _cfg()
    try:
        e["mute"].remove(int(uid))
        return f"🔈 کاربر از میوت خارج شد: {uid} {name}".strip()
    except ValueError:
        return "ℹ️ این کاربر در لیست میوت نبود."

async def clean_mute() -> str:
    e = _cfg()
    e["mute"] = []
    return "🧹 لیست میوت پاک شد."

async def list_mute() -> str:
    e = _cfg()
    arr = e.get("mute", [])
    if not arr:
        return "لیست mute خالی است."
    return "Mute list:\n" + "\n".join(str(x) for x in arr)

# ========================= High-level status/help =============================

async def enemy_status() -> str:
    e = _cfg()
    return (
        "Enemy Status:\n"
        f"- enemy_enabled: {bool(e.get('enemy_enabled', True))}\n"
        f"- enemy_ignore: {int(e.get('enemy_ignore', 0))}\n"
        f"- counters: {len(e.get('enemy_counter', {}))} users\n"
        f"- enemies: {len(e.get('enemy_users', {}))}\n"
        f"- specials: {len(e.get('special_users', {}))}\n"
        f"- mute users: {len(e.get('mute', []))}\n"
        f"- special texts: {len(e.get('specialenemytext', []))}\n"
        f"- special delays: {len(e.get('SPTimelist', []))}"
    )

def help_text() -> str:
    return (
        "دستورات Enemy/Special/Mute:\n"
        "— وضعیت و راهنما —\n"
        "• /enemy_status | /es\n"
        "• /enemy_help | /eh\n"
        "— مدیریت Enemy معمولی —\n"
        "• /addenemy  [ریپلای|@user|uid]\n"
        "• /delenemy  [ریپلای|@user|uid]\n"
        "• /cleanenemy\n"
        "• /enemy_list\n"
        "• /enemy_on | /enemy_off\n"
        "• /enemy_ignore <N>  (بدون آرگومان = نمایش مقدار فعلی)\n"
        "• /enemy_counter get [uid] | reset [all|uid] | top [K]\n"
        "— مدیریت Special —\n"
        "• /addspecial [ریپلای|@user|uid]\n"
        "• /delspecial [ریپلای|@user|uid]\n"
        "• /cleanspecial\n"
        "• /special_list\n"
        "• /atextSPenemy <text> | /rtextSPenemy <text> | /ctextSPenemy\n"
        "• /sp_listtext | /sp_addtext <text> | /sp_deltext <idx> | /sp_cleartext\n"
        "• /SPenemytimes <n1 n2 ...>\n"
        "• /sp_listdelay | /sp_adddelay <sec> | /sp_deldelay <idx> | /sp_cleardelay\n"
        "• /sp_test\n"
        "— مدیریت Mute —\n"
        "• /mute [ریپلای|@user|uid]\n"
        "• /unmute [ریپلای|@user|uid]\n"
        "• /cleanmute\n"
        "• /mute_list"
    )

# ========================= Register handlers ==================================

def register(app: Client) -> None:
    e = _cfg()

    # ====== Help / Status ======
    @app.on_message(admin_filter & filters.command(["enemy_help", "eh"], prefixes=["/", ""]))
    async def _help(client: Client, m: Message):
        await m.reply(help_text())

    @app.on_message(admin_filter & filters.command(["enemy_status", "es"], prefixes=["/", ""]))
    async def _status(client: Client, m: Message):
        await m.reply(await enemy_status())

    # ====== Enable / Disable ======
    @app.on_message(admin_filter & filters.command("enemy_on", prefixes=["/", ""]))
    async def _enemy_on(client: Client, m: Message):
        e["enemy_enabled"] = True
        await m.reply("enemy معمولی فعال شد.")

    @app.on_message(admin_filter & filters.command("enemy_off", prefixes=["/", ""]))
    async def _enemy_off(client: Client, m: Message):
        e["enemy_enabled"] = False
        await m.reply("enemy معمولی غیرفعال شد.")

    # ====== Enemy users ======
    @app.on_message(admin_filter & filters.command("addenemy", prefixes=["/", ""]))
    async def _addenemy(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await add_enemy(uid, name))

    @app.on_message(admin_filter & filters.command("delenemy", prefixes=["/", ""]))
    async def _delenemy(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await del_enemy(uid, name))

    @app.on_message(admin_filter & filters.command("cleanenemy", prefixes=["/", ""]))
    async def _cleanenemy(client: Client, m: Message):
        await m.reply(await clean_enemy())

    @app.on_message(admin_filter & filters.command("enemy_list", prefixes=["/", ""]))
    async def _enemy_list(client: Client, m: Message):
        await m.reply(await list_enemy())

    # enemy_ignore (get/set)
    @app.on_message(admin_filter & filters.command(["enemy_ignore", "ei"], prefixes=["/", ""]))
    async def _enemy_ignore(client: Client, m: Message):
        args = (m.text or "").split()
        if len(args) < 2:
            # نمایش مقدار فعلی
            await m.reply(f"enemy_ignore = {int(e.get('enemy_ignore', 0))}")
            return
        try:
            value = int(args[1])
        except Exception:
            return await m.reply("❌ عدد معتبر بده.")
        await m.reply(await set_enemy_ignore(value))

    # enemy_counter get/reset/top
    @app.on_message(admin_filter & filters.command(["enemy_counter", "ec"], prefixes=["/", ""]))
    async def _enemy_counter(client: Client, m: Message):
        text = (m.text or "").strip()
        args = text.split()
        sub = args[1].lower() if len(args) > 1 else "help"
        counters = e.setdefault("enemy_counter", {})

        if sub == "get":
            uid = None
            if m.reply_to_message and m.reply_to_message.from_user:
                uid = int(m.reply_to_message.from_user.id)
            elif len(args) > 2:
                try: uid = int(args[2])
                except Exception: uid = None
            if uid is None:
                return await m.reply("Usage: /enemy_counter get [uid]  (یا ریپلای کنید)")
            return await m.reply(f"enemy_counter[{uid}] = {int(counters.get(uid, 0))}")

        if sub == "reset":
            uid = None
            if m.reply_to_message and m.reply_to_message.from_user:
                uid = int(m.reply_to_message.from_user.id)
            elif len(args) > 2 and args[2].lower() != "all":
                try: uid = int(args[2])
                except Exception: uid = None
            if uid is None:
                e["enemy_counter"] = {}
                return await m.reply("enemy_counter برای همه صفر شد.")
            counters[uid] = 0
            return await m.reply(f"enemy_counter برای {uid} صفر شد.")

        if sub == "top":
            k = 10
            if len(args) > 2:
                try: k = max(1, int(args[2]))
                except Exception: pass
            if not counters:
                return await m.reply("هیچ شمارنده‌ای موجود نیست.")
            items = sorted(counters.items(), key=lambda kv: kv[1], reverse=True)[:k]
            body = "\n".join(f"{uid}: {val}" for uid, val in items)
            return await m.reply("Top counters:\n" + body)

        return await m.reply("زیر-دستورات: get | reset [all|uid] | top [K]")

    # ====== Special users ======
    @app.on_message(admin_filter & filters.command("addspecial", prefixes=["/", ""]))
    async def _addspecial(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await add_special(uid, name))

    @app.on_message(admin_filter & filters.command("delspecial", prefixes=["/", ""]))
    async def _delspecial(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await del_special(uid, name))

    @app.on_message(admin_filter & filters.command("cleanspecial", prefixes=["/", ""]))
    async def _cleanspecial(client: Client, m: Message):
        await m.reply(await clean_special())

    @app.on_message(admin_filter & filters.command("special_list", prefixes=["/", ""]))
    async def _special_list(client: Client, m: Message):
        await m.reply(await list_special())

    # ====== Special texts ======
    @app.on_message(admin_filter & filters.command("atextSPenemy", prefixes=["/", ""]))
    async def _add_sp_txt_legacy(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await add_special_text(txt))

    @app.on_message(admin_filter & filters.command("rtextSPenemy", prefixes=["/", ""]))
    async def _rm_sp_txt_legacy(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await remove_special_text(txt))

    @app.on_message(admin_filter & filters.command("ctextSPenemy", prefixes=["/", ""]))
    async def _cl_sp_txt_legacy(client: Client, m: Message):
        await m.reply(await clean_special_text())

    # نسخه‌های کامل‌تر با index
    @app.on_message(admin_filter & filters.command(["sp_addtext", "sat"], prefixes=["/", ""]))
    async def _sp_addtext(client: Client, m: Message):
        txt = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        await m.reply(await add_special_text(txt))

    @app.on_message(admin_filter & filters.command(["sp_deltext", "sdt"], prefixes=["/", ""]))
    async def _sp_deltext(client: Client, m: Message):
        parts = (m.text or "").split(maxsplit=1)
        if len(parts) < 2:
            return await m.reply("Usage: /sp_deltext <index>")
        try:
            idx = int(parts[1])
            e_local = _cfg()
            txt = e_local["specialenemytext"][idx]
            # حذف با مقدار دقیق
            e_local["specialenemytext"].pop(idx)
            return await m.reply(f"حذف شد: {txt}")
        except Exception:
            return await m.reply("ایندکس نامعتبر یا لیست خالی.")

    @app.on_message(admin_filter & filters.command(["sp_listtext", "slt"], prefixes=["/", ""]))
    async def _sp_listtext(client: Client, m: Message):
        await m.reply(await list_special_text())

    @app.on_message(admin_filter & filters.command(["sp_cleartext", "sct"], prefixes=["/", ""]))
    async def _sp_cleartext(client: Client, m: Message):
        await m.reply(await clean_special_text())

    # ====== Special delays / times ======
    @app.on_message(admin_filter & filters.command("SPenemytimes", prefixes=["/", ""]))
    async def _sp_times_legacy(client: Client, m: Message):
        tail = m.text.split(None, 1)[1] if (m.text and len(m.command) > 1) else ""
        nums = []
        for p in re.split(r"[\s,]+", tail.strip()):
            if not p:
                continue
            try:
                nums.append(int(p))
            except Exception:
                pass
        await m.reply(await set_special_times(nums))

    @app.on_message(admin_filter & filters.command(["sp_adddelay", "sad"], prefixes=["/", ""]))
    async def _sp_adddelay(client: Client, m: Message):
        parts = (m.text or "").split(maxsplit=1)
        if len(parts) < 2:
            return await m.reply("Usage: /sp_adddelay <seconds>")
        try:
            sec = max(0, int(parts[1]))
        except Exception:
            return await m.reply("عدد نامعتبر.")
        e["SPTimelist"].append(sec)
        await m.reply(f"تاخیر {sec} ثانیه اضافه شد.")

    @app.on_message(admin_filter & filters.command(["sp_deldelay", "sdd"], prefixes=["/", ""]))
    async def _sp_deldelay(client: Client, m: Message):
        parts = (m.text or "").split(maxsplit=1)
        if len(parts) < 2:
            return await m.reply("Usage: /sp_deldelay <index>")
        try:
            idx = int(parts[1])
            val = e["SPTimelist"].pop(idx)
            await m.reply(f"تاخیر {val} حذف شد.")
        except Exception:
            await m.reply("ایندکس نامعتبر یا لیست خالی.")

    @app.on_message(admin_filter & filters.command(["sp_listdelay", "sld"], prefixes=["/", ""]))
    async def _sp_listdelay(client: Client, m: Message):
        await m.reply(await list_special_times())

    @app.on_message(admin_filter & filters.command(["sp_cleardelay", "scd"], prefixes=["/", ""]))
    async def _sp_cleardelay(client: Client, m: Message):
        e["SPTimelist"] = []
        await m.reply("تمام تاخیرهای ویژه پاک شدند.")

    # ====== Mute ======
    @app.on_message(admin_filter & filters.command("mute", prefixes=["/", ""]))
    async def _mute(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await mute_user(uid, name))

    @app.on_message(admin_filter & filters.command("unmute", prefixes=["/", ""]))
    async def _unmute(client: Client, m: Message):
        uid, name = await _resolve_uid_and_name(client, m)
        if not uid: return await m.reply("❌ کاربر پیدا نشد.")
        await m.reply(await unmute_user(uid, name))

    @app.on_message(admin_filter & filters.command("cleanmute", prefixes=["/", ""]))
    async def _clean_mute(client: Client, m: Message):
        await m.reply(await clean_mute())

    @app.on_message(admin_filter & filters.command("mute_list", prefixes=["/", ""]))
    async def _mute_list(client: Client, m: Message):
        await m.reply(await list_mute())

    # ====== Shortcuts/aliases ======
    # برای راحتی چند اسم میانبر هم اضافه شده‌اند:
    @app.on_message(admin_filter & filters.command(["eh"], prefixes=["/", ""]))
    async def _help_alias(client: Client, m: Message): await _help(client, m)

    @app.on_message(admin_filter & filters.command(["es"], prefixes=["/", ""]))
    async def _status_alias(client: Client, m: Message): await _status(client, m)

    @app.on_message(admin_filter & filters.command(["ei"], prefixes=["/", ""]))
    async def _ei_alias(client: Client, m: Message): await _enemy_ignore(client, m)

    @app.on_message(admin_filter & filters.command(["ec"], prefixes=["/", ""]))
    async def _ec_alias(client: Client, m: Message): await _enemy_counter(client, m)

    @app.on_message(admin_filter & filters.command(["sat"], prefixes=["/", ""]))
    async def _sat_alias(client: Client, m: Message): await _sp_addtext(client, m)

    @app.on_message(admin_filter & filters.command(["sdt"], prefixes=["/", ""]))
    async def _sdt_alias(client: Client, m: Message): await _sp_deltext(client, m)

    @app.on_message(admin_filter & filters.command(["slt"], prefixes=["/", ""]))
    async def _slt_alias(client: Client, m: Message): await _sp_listtext(client, m)

    @app.on_message(admin_filter & filters.command(["sct"], prefixes=["/", ""]))
    async def _sct_alias(client: Client, m: Message): await _sp_cleartext(client, m)

    @app.on_message(admin_filter & filters.command(["sad"], prefixes=["/", ""]))
    async def _sad_alias(client: Client, m: Message): await _sp_adddelay(client, m)

    @app.on_message(admin_filter & filters.command(["sdd"], prefixes=["/", ""]))
    async def _sdd_alias(client: Client, m: Message): await _sp_deldelay(client, m)

    @app.on_message(admin_filter & filters.command(["sld"], prefixes=["/", ""]))
    async def _sld_alias(client: Client, m: Message): await _sp_listdelay(client, m)

    @app.on_message(admin_filter & filters.command(["scd"], prefixes=["/", ""]))
    async def _scd_alias(client: Client, m: Message): await _sp_cleardelay(client, m)

    # ====== Quick sanity checker ======
    @app.on_message(admin_filter & filters.command("enemy_ping", prefixes=["/", ""]))
    async def _enemy_ping(client: Client, m: Message):
        await m.reply("pong 🏓 — enemy_commands آماده است.")
