# -*- coding: utf-8 -*-
# File: CliSelf/SBself/moudels/admin/admin_commands.py
#
# مدیریت ادمین‌ها با مدل دو نقشی:
#   - admin_owner  : ادمینِ ویژه (مخفی در نمایش، در لیست ادمین‌ها محسوب نمی‌شود)
#   - admin        : ادمینِ عادی (تنها ادمینی که نمایش داده می‌شود و قابل افزودن/حذف است)
#
# قواعد این ماژول:
#   - در متن خروجی هیچ اشاره‌ای به "اونر/مالک" نمی‌شود.
#   - تمام دستورات این فایل با دسترسی admin_filter قابل اجرا هستند (یعنی هم admin_owner و هم admin می‌توانند اجرا کنند).
#   - اگر در حذف، شناسهٔ admin_owner داده شود، پاسخ: «این ادمین پیدا نشد.» (چون در لیست ادمین‌ها نیست).
#   - نمایش لیست تنها «ادمین عادی» را نشان می‌دهد. admin_owner مخفی است و هرگز نمایش داده نمی‌شود.
#
# استفاده در main.py (مقداردهی نمونه):
#   from SBself.config import AllConfig
#   AllConfig.setdefault("auth", {})
#   AllConfig["auth"]["admin_owner_id"] = 1111111111   # ادمینِ ویژه (مخفی)
#   AllConfig["auth"]["admin_id"]       = 2222222222   # ادمین عادی
#   AllConfig["auth"]["names"]          = {1111111111: "A.O", 2222222222: "Admin"}  # اختیاری
#
# رجیستر:
#   from SBself.moudels.admin.admin_commands import register as register_admin_commands
#   register_admin_commands(app)

from __future__ import annotations

from typing import Optional, Tuple
from pyrogram import Client, filters
from pyrogram.types import Message

from SBself.config import AllConfig
from SBself.filters.SBfilters import admin_filter  # هر دو نقش (admin_owner و admin) عبور می‌کنند


# ---------------- Helpers ----------------

def _auth() -> dict:
    """اطمینان از وجود ساختار نقش‌ها در کانفیگ."""
    a = AllConfig.setdefault("auth", {})
    a.setdefault("admin_owner_id", None)  # ادمینِ ویژه (در نمایش مخفی است)
    a.setdefault("admin_id", None)        # ادمین عادی (نمایش داده می‌شود)
    a.setdefault("names", {})             # نقشهٔ نامِ نمایشی (اختیاری)
    return a

def _set_admin(uid: Optional[int], name: str = "") -> None:
    """تنظیم/جایگزینی ادمین عادی."""
    a = _auth()
    a["admin_id"] = int(uid) if uid is not None else None
    if uid is not None and name:
        try:
            a["names"][int(uid)] = name
        except Exception:
            pass

def _get_names() -> dict:
    return _auth().setdefault("names", {})

async def _resolve_reply_user(m: Message) -> Tuple[Optional[int], str]:
    """اگر روی پیام کسی ریپلای شده باشد، (id, name) او را برمی‌گرداند؛ وگرنه (None, '')."""
    if not (m.reply_to_message and m.reply_to_message.from_user):
        return None, ""
    u = m.reply_to_message.from_user
    full = " ".join([p for p in [(u.first_name or ""), (u.last_name or "")] if p]).strip()
    return int(u.id), (full or (u.username or "") or "")

async def _edit_or_reply(m: Message, text: str):
    """اول تلاش می‌کند ادیت کند؛ اگر نشد ریپلای می‌دهد."""
    try:
        await m.edit_text(text, disable_web_page_preview=True)
    except Exception:
        await m.reply(text, disable_web_page_preview=True)


# --------------- Business ops ---------------

async def add_admin(uid: int, name: str) -> str:
    """
    تنظیم/جایگزینی ادمین عادی.
    اگر uid همان admin_owner باشد، صرفاً اطلاع می‌دهیم که او در لیست ادمین عادی قرار نمی‌گیرد.
    """
    label = f" — {name}" if name else ""
    return f"✅ ادمین تنظیم شد: `{uid}`{label}"

async def del_admin(uid: int, name: str) -> str:
    """
    حذف ادمین عادی.
    اگر uid همان admin_owner باشد، پیام می‌دهیم «این ادمین پیدا نشد.»
    چون ادمین‌ویژه در لیست ادمین‌های عادی اصلاً وجود ندارد.
    """
    a = _auth()
    admin_owner_id = a.get("admin_owner_id")
    if admin_owner_id is not None and int(uid) == int(admin_owner_id):
        return "ℹ️ این ادمین پیدا نشد."

    curr_admin = a.get("admin_id")
    if curr_admin is None:
        return "ℹ️ ادمینی برای حذف ثبت نشده."
    if int(uid) != int(curr_admin):
        return "ℹ️ این ادمین پیدا نشد."

    # حذف ادمین عادی
    a["admin_id"] = None
    _get_names().pop(int(uid), None)
    label = f" — {name}" if name else ""
    return f"🗑 ادمین حذف شد: `{uid}`{label}"

async def clean_admins() -> str:
    """پاکسازی ادمین عادی (ادمین‌ویژه اصلاً در این لیست نیست که بخواهد پاک شود)."""
    a = _auth()
    curr_admin = a.get("admin_id")
    a["admin_id"] = None
    if curr_admin is not None:
        _get_names().pop(int(curr_admin), None)
    return "🧹 ادمین پاک شد."

async def list_admins() -> str:
    """
    نمایش لیست ادمین‌ها:
      - فقط «ادمین عادی» نمایش داده می‌شود.
      - ادمین‌ویژه (admin_owner) هرگز نمایش داده نمی‌شود.
    """
    a = _auth()
    admin_id = a.get("admin_id")
    names = _get_names()

    lines = ["👮‍♂️ **لیست ادمین‌ها:**"]
    if admin_id:
        nm = names.get(int(admin_id), "")
        lines.append(f"- `{admin_id}`{(' — ' + nm) if nm else ''}")
    else:
        lines.append("ℹ️ ادمین ثبت نشده است.")
    return "\n".join(lines)

async def help_text() -> str:
    return (
        "📖 راهنمای مدیریت ادمین:\n"
        "• /addadmin   (ریپلای روی پیام فرد) — تنظیم/جایگزینی ادمین\n"
        "• /deladmin   (ریپلای) — حذف ادمین\n"
        "• /cleanadmins — پاکسازی ادمین\n"
        "• /admins — نمایش لیست ادمین‌ها\n"
        "• /admin_help\n"
    )


# --------------- Registrar ---------------

def register(app: Client) -> None:
    # تمام دستورات با admin_filter در دسترس‌اند (هم ادمین‌ویژه و هم ادمین عادی می‌توانند اجرا کنند)

    @app.on_message(admin_filter & filters.command("addadmin", prefixes=["/", ""]))
    async def _add_admin_cmd(client: Client, m: Message):
        uid, name = await _resolve_reply_user(m)
        if not uid:
            return await _edit_or_reply(m, "❗روی پیام فرد مورد نظر ریپلای بزن.")
        msg = await add_admin(uid, name)
        AllConfig["auth"]["admin_id"] = uid
        await _edit_or_reply(m, msg)

    @app.on_message(admin_filter & filters.command("deladmin", prefixes=["/", ""]))
    async def _del_admin_cmd(client: Client, m: Message):
        uid, name = await _resolve_reply_user(m)
        if not uid:
            return await _edit_or_reply(m, "❗روی پیام فرد مورد نظر ریپلای بزن.")
        msg = await del_admin(uid, name)
        await _edit_or_reply(m, msg)

    @app.on_message(admin_filter & filters.command("cleanadmins", prefixes=["/", ""]))
    async def _clean_admins_cmd(client: Client, m: Message):
        msg = await clean_admins()
        await _edit_or_reply(m, msg)

    @app.on_message(admin_filter & filters.command(["admins", "showadmins"], prefixes=["/", ""]))
    async def _list_admins_cmd(client: Client, m: Message):
        msg = await list_admins()
        await _edit_or_reply(m, msg)
