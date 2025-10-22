# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/admin_manager.py

from ...config import AllConfig, adminList

# تلاش برای استفاده از logger پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("admin_manager")
except Exception:
    import logging
    logger = logging.getLogger("admin_manager")


# -------------------------------
# ➕ افزودن ادمین جدید
# -------------------------------
async def add_admin(user_id: int, username: str = None) -> str:
    admins = AllConfig["admin"].get("admins", [])
    if user_id in admins:
        return "⚠️ این کاربر از قبل ادمین است."

    admins.append(user_id)
    AllConfig["admin"]["admins"] = admins
    adminList.append(user_id)

    logger.info(f"✅ Admin added: {user_id} ({username})")
    return f"✅ {username or user_id} به لیست ادمین‌ها اضافه شد."


# -------------------------------
# 🗑️ حذف ادمین
# -------------------------------
async def del_admin(user_id: int, username: str = None) -> str:
    admins = AllConfig["admin"].get("admins", [])
    if user_id not in admins:
        return "❌ این کاربر در لیست ادمین‌ها نیست."

    admins.remove(user_id)
    AllConfig["admin"]["admins"] = admins
    if user_id in adminList:
        adminList.remove(user_id)

    logger.info(f"🗑️ Admin removed: {user_id} ({username})")
    return f"🗑️ {username or user_id} از لیست ادمین‌ها حذف شد."


# -------------------------------
# 🧹 پاکسازی کل لیست ادمین‌ها
# -------------------------------
async def clean_admins(admins=None) -> str:
    AllConfig["admin"]["admins"] = []
    adminList.clear()
    logger.info("🧹 All admins cleared.")
    return "🧹 لیست ادمین‌ها پاکسازی شد."


# -------------------------------
# 👮‍♂️ نمایش لیست ادمین‌ها
# -------------------------------
async def show_admins(client=None) -> str:
    admins = AllConfig["admin"].get("admins", [])
    if not admins:
        return "👮‍♂️ هیچ ادمینی ثبت نشده است."

    text = "👮‍♂️ **لیست ادمین‌ها:**\n"
    for i, user_id in enumerate(admins, 1):
        try:
            if client:
                user = await client.get_users(user_id)
                name = user.first_name or user.username or str(user_id)
            else:
                name = str(user_id)
            text += f"{i}. {name} (`{user_id}`)\n"
        except Exception:
            text += f"{i}. `{user_id}`\n"

    logger.info("✅ Admin list displayed.")
    return text
