# -*- coding: utf-8 -*-
# File: SBself/filters/SBfilters.py
#
# فیلترهای دسترسی و کمکی پروژه
# ─────────────────────────────────────────────────────────
# نقش‌ها (ساده و شفاف):
#   - Owner-Admin: مدیر اصلی با دسترسی ویژه به تمام دستورات (مثل get_code)
#   - Admin:       ادمین عادی با دسترسی عمومی مدیرها
#
# مقداردهی در main.py (نمونه):
#   from SBself.config import AllConfig
#   AllConfig.setdefault("auth", {})
#   AllConfig["auth"]["owner_admin_id"] = 1111111111  # ادمین-اونر
#   AllConfig["auth"]["admin_id"]       = 2222222222  # ادمین عادی
#
# فیلترهای ارائه‌شده در این فایل:
#   - admin_filter         → Owner-Admin یا Admin
#   - owner_admin_only     → فقط Owner-Admin (برای دستورات ویژه)
#   - only_reply_to_me     → فقط اگر پیام ورودی روی «پیام خودِ من» ریپلای شده باشد
#   - timer_auto_filter    → True وقتی AllConfig["timer"]["auto"] == True
#
# توجه: اگر قبلاً فیلترهای دیگری داشتید، می‌توانید آن‌ها را اینجا ادغام کنید.

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message

from SBself.config import AllConfig


# ─────────────────────────────────────────────────────────
# ابزارهای نقش‌ها
# ─────────────────────────────────────────────────────────

def _auth() -> dict:
    """اطمینان از وجود ساختار auth و ارائه‌ی مقادیر پیش‌فرض."""
    a = AllConfig.setdefault("auth", {})
    a.setdefault("owner_admin_id", None)
    a.setdefault("admin_id", None)
    return a


def _is_owner_admin(user_id: int) -> bool:
    auth = _auth()
    return bool(user_id) and (auth.get("owner_admin_id") == user_id)


def _is_admin(user_id: int) -> bool:
    auth = _auth()
    return bool(user_id) and (auth.get("admin_id") == user_id)


# ─────────────────────────────────────────────────────────
# بدنه‌ی فیلترهای دسترسی
# ─────────────────────────────────────────────────────────

def _admin_any(_, __, m: Message) -> bool:
    """
    اجازه‌ی دسترسی ادمینی:
      - Owner-Admin یا Admin
    """
    try:
        if not m.from_user:
            return False
        uid = int(m.from_user.id)
        return _is_owner_admin(uid) or _is_admin(uid)
    except Exception:
        return False


def _owner_admin_only(_, __, m: Message) -> bool:
    """
    فقط Owner-Admin (برای دستورات حساس مانند get_code).
    """
    try:
        if not m.from_user:
            return False
        uid = int(m.from_user.id)
        return _is_owner_admin(uid)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────
# فیلتر فقط اگر روی «پیام خودم» ریپلای شده باشد
# ─────────────────────────────────────────────────────────

def _only_reply_to_me(_, __, message: Message) -> bool:
    """
    True اگر پیام ورودی روی پیامی ریپلای شده باشد که فرستنده‌اش خودِ کلاینت است.
    تشخیص با:
      - reply_to_message.from_user.is_self == True  (حالت رایج)
      - یا reply_to_message.outgoing == True        (fallback)
    """
    try:
        r = message.reply_to_message
        if not r:
            return False

        if getattr(r, "from_user", None) and getattr(r.from_user, "is_self", False):
            return True

        if getattr(r, "outgoing", False):
            return True

        return False
    except Exception:
        return False


# ─────────────────────────────────────────────────────────
# فیلتر وضعیت Auto در تایمر: AllConfig["timer"]["auto"] == True
# ─────────────────────────────────────────────────────────

def _timer_auto_enabled(_, __, message: Message) -> bool:
    """
    True وقتی Auto Scheduler روشن باشد.
    """
    try:
        return bool(AllConfig.setdefault("timer", {}).get("auto", False))
    except Exception:
        return False


# ─────────────────────────────────────────────────────────
# اکسپورت فیلترهای Pyrogram
# ─────────────────────────────────────────────────────────

admin_filter       = filters.create(_admin_any, "admin_filter")
owner_admin_only   = filters.create(_owner_admin_only, "owner_admin_only")
only_reply_to_me   = filters.create(_only_reply_to_me, "only_reply_to_me")
timer_auto_filter  = filters.create(_timer_auto_enabled, "timer_auto_filter")
