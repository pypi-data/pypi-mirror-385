# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/show_manager.py

from ..config import AllConfig

# تلاش برای استفاده از logger اصلی پروژه
try:
    from core.logger import get_logger
    logger = get_logger("show_manager")
except Exception:
    import logging
    logger = logging.getLogger("show_manager")


# -------------------------------
# نمایش لیست دشمن‌ها
# -------------------------------
async def show_enemy() -> str:
    enemies = AllConfig["enemy"].get("enemy", [])
    specials = AllConfig["enemy"].get("special_enemy", [])

    if not enemies and not specials:
        return "😇 دشمنی ثبت نشده."

    text = "😈 **لیست دشمن‌ها:**\n"
    for i, e in enumerate(enemies, 1):
        text += f"{i}. `{e}`\n"

    if specials:
        text += "\n💀 **دشمنان ویژه:**\n"
        for i, s in enumerate(specials, 1):
            text += f"{i}. `{s}`\n"

    logger.info("✅ Enemy list displayed.")
    return text


# -------------------------------
# نمایش لیست کاربران بی‌صدا (mute)
# -------------------------------
async def show_mute() -> str:
    muted = AllConfig["enemy"].get("mute", [])
    if not muted:
        return "🔇 لیست بی‌صدا خالی است."
    text = "🔇 **لیست کاربران بی‌صدا:**\n"
    for i, u in enumerate(muted, 1):
        text += f"{i}. `{u}`\n"
    logger.info("✅ Mute list displayed.")
    return text


# -------------------------------
# نمایش لیست گروه‌های فعال منشن
# -------------------------------
async def show_group() -> str:
    groups = AllConfig["mention"].get("group_ids", [])
    if not groups:
        return "👥 هیچ گروهی ثبت نشده."
    text = "👥 **لیست گروه‌های فعال برای منشن:**\n"
    for i, g in enumerate(groups, 1):
        text += f"{i}. `{g}`\n"
    logger.info("✅ Group list displayed.")
    return text


# -------------------------------
# نمایش لیست ادمین‌ها
# -------------------------------
async def show_admins(client=None) -> str:
    admins = AllConfig["admin"].get("admins", [])
    if not admins:
        return "👮‍♂️ هیچ ادمینی ثبت نشده."
    text = "👮‍♂️ **لیست ادمین‌ها:**\n"
    for i, a in enumerate(admins, 1):
        text += f"{i}. `{a}`\n"
    logger.info("✅ Admin list displayed.")
    return text
