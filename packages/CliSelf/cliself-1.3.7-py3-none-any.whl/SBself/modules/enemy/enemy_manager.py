# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/enemy_manager.py

from ...config import AllConfig

try:
    from ...core.logger import get_logger
    logger = get_logger("enemy_manager")
except Exception:
    import logging
    logger = logging.getLogger("enemy_manager")


# -------------------------------
# 😈 دشمن‌های عادی
# -------------------------------
async def add_enemy(user_id: int, username: str = None) -> str:
    enemies = AllConfig["enemy"].get("enemy", [])
    if user_id in enemies:
        return "⚠️ این کاربر از قبل دشمن است."
    enemies.append(user_id)
    AllConfig["enemy"]["enemy"] = enemies
    logger.info(f"😈 Enemy added: {user_id} ({username})")
    return f"😈 {username or user_id} به لیست دشمن‌ها اضافه شد."


async def del_enemy(user_id: int, username: str = None) -> str:
    enemies = AllConfig["enemy"].get("enemy", [])
    if user_id not in enemies:
        return "❌ این کاربر در لیست دشمن‌ها نیست."
    enemies.remove(user_id)
    AllConfig["enemy"]["enemy"] = enemies
    logger.info(f"🗑️ Enemy removed: {user_id} ({username})")
    return f"🗑️ {username or user_id} از لیست دشمن‌ها حذف شد."


async def clean_enemy() -> str:
    AllConfig["enemy"]["enemy"] = []
    logger.info("🧹 Enemy list cleared.")
    return "🧹 لیست دشمن‌ها پاکسازی شد."


async def set_enemy_ignore(value: int) -> str:
    AllConfig["enemy"]["enemy_ignore"] = value
    logger.info(f"🚫 Enemy ignore set to {value}")
    return f"🚫 سطح نادیده‌گیری دشمن‌ها روی {value} تنظیم شد."


# -------------------------------
# 💀 دشمنان ویژه
# -------------------------------
async def add_special(user_id: int, username: str = None) -> str:
    specials = AllConfig["enemy"].get("special_enemy", [])
    if user_id in specials:
        return "⚠️ این کاربر از قبل دشمن ویژه است."
    specials.append(user_id)
    AllConfig["enemy"]["special_enemy"] = specials
    logger.info(f"💀 Special enemy added: {user_id} ({username})")
    return f"💀 {username or user_id} به لیست دشمنان ویژه اضافه شد."


async def del_special(user_id: int, username: str = None) -> str:
    specials = AllConfig["enemy"].get("special_enemy", [])
    if user_id not in specials:
        return "❌ این کاربر در لیست دشمنان ویژه نیست."
    specials.remove(user_id)
    AllConfig["enemy"]["special_enemy"] = specials
    logger.info(f"🗑️ Special enemy removed: {user_id} ({username})")
    return f"🗑️ {username or user_id} از لیست دشمنان ویژه حذف شد."


async def clean_special() -> str:
    AllConfig["enemy"]["special_enemy"] = []
    logger.info("🧹 Special enemy list cleared.")
    return "🧹 لیست دشمنان ویژه پاکسازی شد."


# -------------------------------
# 🗨️ پیام‌های دشمن ویژه
# -------------------------------
async def add_special_text(text: str) -> str:
    if not text.strip():
        return "❌ متن وارد نشده."
    texts = AllConfig["enemy"].get("specialenemytext", [])
    texts.append(text.strip())
    AllConfig["enemy"]["specialenemytext"] = texts
    logger.info(f"💬 Added special enemy text: {text.strip()}")
    return "💬 متن جدید برای دشمنان ویژه اضافه شد."


async def remove_special_text(text: str) -> str:
    texts = AllConfig["enemy"].get("specialenemytext", [])
    if text not in texts:
        return "❌ چنین متنی در لیست وجود ندارد."
    texts.remove(text)
    AllConfig["enemy"]["specialenemytext"] = texts
    logger.info(f"🗑️ Removed special enemy text: {text}")
    return "🗑️ متن از لیست دشمنان ویژه حذف شد."


async def clean_special_text() -> str:
    AllConfig["enemy"]["specialenemytext"] = []
    logger.info("🧹 Cleared all special enemy texts.")
    return "🧹 تمام متن‌های دشمنان ویژه پاکسازی شدند."


# -------------------------------
# ⏱️ زمان‌بندی پاسخ دشمنان ویژه
# -------------------------------
async def set_special_times(times: list) -> str:
    if not times or not all(str(t).isdigit() for t in times):
        return "❌ لیست زمان معتبر نیست (باید فقط عدد باشد)."
    AllConfig["enemy"]["SPTimelist"] = [int(t) for t in times]
    logger.info(f"🕓 Special enemy times set: {times}")
    return f"🕓 زمان‌های پاسخ دشمنان ویژه تنظیم شد ({times})."


# -------------------------------
# 🔇 بی‌صدا کردن دشمنان
# -------------------------------
async def mute_user(user_id: int, username: str = None) -> str:
    mutes = AllConfig["enemy"].get("mute", [])
    if user_id in mutes:
        return "⚠️ این کاربر از قبل بی‌صداست."
    mutes.append(user_id)
    AllConfig["enemy"]["mute"] = mutes
    logger.info(f"🔇 Muted user: {user_id} ({username})")
    return f"🔇 {username or user_id} بی‌صدا شد."


async def unmute_user(user_id: int, username: str = None) -> str:
    mutes = AllConfig["enemy"].get("mute", [])
    if user_id not in mutes:
        return "❌ این کاربر در لیست بی‌صداها نیست."
    mutes.remove(user_id)
    AllConfig["enemy"]["mute"] = mutes
    logger.info(f"🔊 Unmuted user: {user_id} ({username})")
    return f"🔊 {username or user_id} از بی‌صدا خارج شد."


async def clean_mute() -> str:
    AllConfig["enemy"]["mute"] = []
    logger.info("🧹 Cleared all muted users.")
    return "🧹 لیست کاربران بی‌صدا پاکسازی شد."
