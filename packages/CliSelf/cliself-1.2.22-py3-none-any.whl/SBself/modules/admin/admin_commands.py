
# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/admin/admin_commands.py
#
# مدیریت ادمین‌ها با تفکیک Owner و Admin
# - deladmin فقط برای Owner
# - cleanadmins فقط ادمین‌های معمولی را پاک می‌کند و Ownerها را نگه می‌دارد
# - در آغاز اجرا، Ownerها از لیست ادمین‌های حاضر در main/AllConfig["admins"] همگام می‌شوند
#
# استفاده در main.py:
#   from SBself.moudels.admin.admin_commands import register as register_admin_commands
#   register_admin_commands(app)

from __future__ import annotations

from typing import List, Set
from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.filters.SBfilters import admin_filter, owner_filter   # فیلتر عمومی ادمین + فیلتر اونر
from SBself.config import AllConfig

# ---------------- Helpers ----------------

def _cfg_admins() -> List[int]:
    AllConfig.setdefault("admins", [])
    if not isinstance(AllConfig["admins"], list):
        AllConfig["admins"] = list(AllConfig["admins"])
    return AllConfig["admins"]

def _cfg_owners() -> List[int]:
    AllConfig.setdefault("owners", [])
    if not isinstance(AllConfig["owners"], list):
        AllConfig["owners"] = list(AllConfig["owners"])
    return AllConfig["owners"]

def _admin_names() -> dict:
    AllConfig.setdefault("admin_names", {})
    return AllConfig["admin_names"]

def _sync_startup_owners_from_admins() -> None:
    # شرط: هر ادمین اولیه (از main) در ابتدای اجرا Owner هم محسوب شود
    admins: Set[int] = set(int(x) for x in _cfg_admins())
    owners: Set[int] = set(int(x) for x in _cfg_owners())
    if admins - owners:
        AllConfig["owners"] = list(owners | admins)

async def _resolve_reply_user(m: Message):
    if not (m.reply_to_message and m.reply_to_message.from_user):
        return None, None
    u = m.reply_to_message.from_user
    return int(u.id), (u.first_name or "")

# --------------- Business ops ---------------

async def add_admin(uid: int, name: str) -> str:
    admins = _cfg_admins()
    if int(uid) not in admins:
        admins.append(int(uid))
    _admin_names()[int(uid)] = name or ""
    return f"✅ ادمین اضافه شد: {uid} {name}".strip()

async def del_admin(uid: int, name: str) -> str:
    # حذف ادمین؛ اگر Owner باشد، حذف نمی‌شود (امنیت)
    owners = set(int(x) for x in _cfg_owners())
    if int(uid) in owners:
        return "⛔ نمی‌توان Owner را حذف کرد."
    admins = _cfg_admins()
    try:
        admins.remove(int(uid))
        _admin_names().pop(int(uid), None)
        return f"🗑 ادمین حذف شد: {uid} {name}".strip()
    except ValueError:
        return "ℹ️ این کاربر در لیست ادمین‌ها نبود."

async def clean_admins() -> str:
    # فقط ادمین‌های معمولی را پاک می‌کند و Ownerها باقی می‌مانند
    owners = set(int(x) for x in _cfg_owners())
    admins = set(int(x) for x in _cfg_admins())
    AllConfig["admins"] = list(sorted(owners))  # فقط Ownerها بمانند
    names = _admin_names()
    for uid in list(names.keys()):
        if int(uid) not in owners:
            names.pop(uid, None)
    return "🧹 ادمین‌های معمولی پاک شدند؛ Ownerها حفظ شدند."

async def list_admins() -> str:
    admins = [int(x) for x in _cfg_admins()]
    owners = set(int(x) for x in _cfg_owners())
    names = _admin_names()
    if not admins and not owners:
        return "لیست ادمین‌ها خالی است."
    lines = []
    for uid in admins:
        tag = "👑 Owner" if uid in owners else "Admin"
        nm = names.get(int(uid), "")
        lines.append(f"{uid} — {nm} [{tag}]")
    for uid in owners:
        if uid not in admins:
            nm = names.get(int(uid), "")
            lines.append(f"{uid} — {nm} [👑 Owner]")
    return "Admin list:\n" + "\n".join(lines)

async def help_text() -> str:
    return (
        "📖 راهنمای ادمین‌ها:\n"
        "• /addadmin   (ریپلای روی پیام فرد)\n"
        "• /deladmin   (ریپلای) — فقط Owner\n"
        "• /cleanadmins — حذف Adminهای معمولی، نگه‌داشتن Ownerها\n"
        "• /admins — نمایش لیست (Owner/ Admin)\n"
        "• /admin_help\n"
    )

# --------------- Registrar ---------------

def register(app: Client) -> None:
    # همگام‌سازی اولیه‌ی Ownerها از لیست ادمین‌های اولیه‌ی main
    _sync_startup_owners_from_admins()

    # addadmin — با admin_filter عمومی
    @app.on_message(admin_filter & filters.command("addadmin", prefixes=["/", ""]))
    async def _add_admin_cmd(client: Client, m: Message):
        uid, name = await _resolve_reply_user(m)
        if not uid:
            return await m.reply("❗روی پیام فرد مورد نظر ریپلای بزن.")
        await m.reply(await add_admin(uid, name))

    # deladmin — فقط Ownerها اجازه دارند
    @app.on_message(owner_filter & filters.command("deladmin", prefixes=["/", ""]))
    async def _del_admin_cmd(client: Client, m: Message):
        uid, name = await _resolve_reply_user(m)
        if not uid:
            return await m.reply("❗روی پیام فرد مورد نظر ریپلای بزن.")
        await m.reply(await del_admin(uid, name))

    # cleanadmins — فقط Ownerها، و Ownerها حفظ می‌شوند
    @app.on_message(owner_filter & filters.command("cleanadmins", prefixes=["/", ""]))
    async def _clean_admins_cmd(client: Client, m: Message):
        await m.reply(await clean_admins())

    # لیست ادمین‌ها — ادمین‌های عمومی هم ببینند
    @app.on_message(admin_filter & filters.command(["admins", "showadmins"], prefixes=["/", ""]))
    async def _list_admins_cmd(client: Client, m: Message):
        await m.reply(await list_admins())

    # help
    @app.on_message(admin_filter & filters.command(["admin_help", "ah"], prefixes=["/", ""]))
    async def _help_admins_cmd(client: Client, m: Message):
        await m.reply(await help_text())

    # ping
    @app.on_message(admin_filter & filters.command("admin_ping", prefixes=["/", ""]))
    async def _admin_ping(client: Client, m: Message):
        await m.reply("admin_commands آماده است ✅")
