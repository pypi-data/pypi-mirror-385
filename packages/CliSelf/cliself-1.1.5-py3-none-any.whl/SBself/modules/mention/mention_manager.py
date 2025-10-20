# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/mention_manager.py

from ...config import AllConfig

# تلاش برای استفاده از logger پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("mention_manager")
except Exception:
    import logging
    logger = logging.getLogger("mention_manager")


# -------------------------------
# ✍️ تنظیم متن منشن
# -------------------------------
async def set_mention_text(text: str) -> str:
    if not text.strip():
        return "❌ متن منشن نمی‌تواند خالی باشد."
    AllConfig["mention"]["textMen"] = text.strip()
    logger.info(f"✅ Mention text set: {text.strip()}")
    return "✅ متن منشن تنظیم شد."


# -------------------------------
# 🆔 تنظیم شناسه کاربر برای منشن
# -------------------------------
async def set_mention_user(user_id: int) -> str:
    if not user_id:
        return "❌ شناسه کاربر معتبر نیست."
    AllConfig["mention"]["useridMen"] = user_id
    logger.info(f"✅ Mention target set: {user_id}")
    return f"✅ کاربر {user_id} برای منشن تنظیم شد."


# -------------------------------
# ⚙️ فعال / غیرفعال کردن منشن خودکار
# -------------------------------
async def toggle_mention(enable: bool) -> str:
    AllConfig["mention"]["is_menshen"] = enable
    logger.info(f"🔄 Auto mention {'enabled' if enable else 'disabled'}.")
    return "✅ منشن خودکار فعال شد." if enable else "🛑 منشن خودکار غیرفعال شد."


# -------------------------------
# 👥 افزودن گروه به لیست منشن
# -------------------------------
async def add_group(group_id: int) -> str:
    groups = AllConfig["mention"]["group_ids"]
    if group_id in groups:
        return "⚠️ این گروه از قبل ثبت شده است."
    groups.append(group_id)
    logger.info(f"✅ Group added to mention list: {group_id}")
    return f"✅ گروه `{group_id}` به لیست گروه‌های منشن اضافه شد."


# -------------------------------
# ❌ حذف گروه از لیست منشن
# -------------------------------
async def remove_group(group_id: int) -> str:
    groups = AllConfig["mention"]["group_ids"]
    if group_id not in groups:
        return "❌ این گروه در لیست منشن نیست."
    groups.remove(group_id)
    logger.info(f"🗑️ Group removed from mention list: {group_id}")
    return f"🗑️ گروه `{group_id}` از لیست منشن حذف شد."


# -------------------------------
# 🧹 پاکسازی کامل گروه‌های منشن
# -------------------------------
async def clear_groups() -> str:
    AllConfig["mention"]["group_ids"] = []
    logger.info("🧹 All mention groups cleared.")
    return "🧹 تمام گروه‌های منشن حذف شدند."


# -------------------------------
# 📊 وضعیت فعلی منشن
# -------------------------------
async def mention_status() -> str:
    mention_cfg = AllConfig["mention"]
    text = mention_cfg.get("textMen", "")
    user_id = mention_cfg.get("useridMen", "")
    enabled = mention_cfg.get("is_menshen", False)
    groups = mention_cfg.get("group_ids", [])

    msg = (
        "📋 **وضعیت منشن:**\n"
        f"💬 متن منشن: {text or '—'}\n"
        f"🎯 کاربر هدف: `{user_id or '—'}`\n"
        f"⚙️ فعال: {'✅' if enabled else '❌'}\n"
        f"👥 گروه‌ها: {len(groups)}\n"
    )

    if groups:
        msg += "\n🗂 **لیست گروه‌ها:**\n"
        msg += "\n".join([f"- `{gid}`" for gid in groups])

    logger.info("📊 Mention status displayed.")
    return msg
