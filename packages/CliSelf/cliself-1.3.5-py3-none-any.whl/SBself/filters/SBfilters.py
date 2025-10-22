# -*- coding: utf-8 -*-
# File: CliSelf/SBself/filters/SBfilters.py

from pyrogram import filters
from ..config import AllConfig 
from pyrogram.types import Message

def _only_reply_to_me(_, __, message: Message) -> bool:
    """
    True اگر:
      - پیام «reply_to_message» داشته باشد، و
      - پیامِ ریپلای‌شده توسط خودِ کلاینت ارسال شده باشد.
    روش تشخیص:
      - reply_to_message.from_user.is_self == True  (اکثر مواقع)
      - یا reply_to_message.outgoing == True        (fallback امن برای userbot)
    """
    try:
        r = message.reply_to_message
        if not r:
            return False

        # حالت معمول: پیام ریپلای‌شده از نوع کاربری است و از خودِ من است
        if getattr(r, "from_user", None) and getattr(r.from_user, "is_self", False):
            return True

        # fallback: بعضی مواقع from_user در دسترس نیست اما outgoing ست است
        if getattr(r, "outgoing", False):
            return True

        # در غیر این صورت، ریپلای به پیامِ من نیست
        return False
    except Exception:
        return False


# فیلتر قابل استفاده در هندلرها:

def _is_owner(msg) -> bool:
    try:
        uid = int(msg.from_user.id) if msg.from_user else None
    except Exception:
        uid = None
    if uid is None:
        return False
    owners = AllConfig.get("owners", [])
    return uid in owners

def _timer_auto_enabled(_, __, message: Message) -> bool:
    """
    اگر در کانفیگ، AllConfig["timer"]["auto"] مقدار True داشته باشد → True.
    در غیر اینصورت یا در خطاها → False.
    """
    try:
        return bool(AllConfig.setdefault("timer", {}).get("auto", False))
    except Exception:
        return False



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
timer_auto_filter  = filters.create(_timer_auto_enabled, "timer_auto_filter")
owner_filter = filters.create(lambda _, __, m: _is_owner(m))
timer_auto_filter = filters.create(_timer_auto_enabled, "timer_auto_filter")
# 💀 فیلتر دشمنان ویژه
special_enemy_filter = filters.create(
    lambda _, __, m: (
        m.from_user
        and m.from_user.id in AllConfig["enemy"].get("special_enemy", [])
    )
)

# 😈 فیلتر دشمنان معمولی
enemy_filter = filters.create(
    lambda _, __, m: (
        m.from_user
        and m.from_user.id in AllConfig["enemy"].get("enemy", [])
    )
)

# 🔇 فیلتر کاربران بی‌صدا
mute_filter = filters.create(
    lambda _, __, m: (
        m.from_user
        and m.from_user.id in AllConfig["enemy"].get("mute", [])
    )
)

# 👮‍♂️ فیلتر ادمین‌ها
admin_filter = filters.create(
    lambda _, __, m: (
        m.from_user and (
            m.from_user.id in AllConfig.get("admin", {}).get("admins", [])
            or m.from_user.id in AllConfig.get("admins", [])           
            or m.from_user.id in AllConfig.get("owners", [])           
        )
    )
)

only_reply_to_me = filters.create(_only_reply_to_me, "only_reply_to_me")