# -*- coding: utf-8 -*-
# File: CliSelf/SBself/filters/SBfilters.py

from pyrogram import filters
from ..config import AllConfig

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