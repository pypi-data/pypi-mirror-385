# -*- coding: utf-8 -*-
# File: CliSelf/SBself/filters/SBfilters.py

from pyrogram import filters
from ..config import AllConfig
from __future__ import annotations
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
only_reply_to_me = filters.create(_only_reply_to_me, "only_reply_to_me")

def _is_owner(msg) -> bool:
    try:
        uid = int(msg.from_user.id) if msg.from_user else None
    except Exception:
        uid = None
    if uid is None:
        return False
    owners = AllConfig.get("owners", [])
    return uid in owners

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


owner_filter = filters.create(lambda _, __, m: _is_owner(m))