# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/name_manager.py

import asyncio
from ..config import AllConfig

# تلاش برای استفاده از logger اصلی پروژه
try:
    from ..core.logger import get_logger
    logger = get_logger("name_manager")
except Exception:
    import logging
    logger = logging.getLogger("name_manager")


# -------------------------------
# 🧠 مقداردهی اولیه مدیریت نام‌ها
# -------------------------------
def init_name_manager(app):
    """
    آماده‌سازی سیستم تغییر خودکار نام‌ها و اتصال کلاینت اصلی.
    """
    AllConfig["names"]["app"] = app
    AllConfig["names"]["changenames_task"] = None
    logger.info("✅ Name manager initialized.")


# -------------------------------
# ➕ افزودن چند نام جدید
# -------------------------------
async def nm_set_names(names_text: str) -> str:
    """
    افزودن چند نام جدید به لیست تغییر خودکار.
    """
    names = [n.strip() for n in names_text.splitlines() if n.strip()]
    if not names:
        return "❌ نامی برای افزودن وارد نشده."

    AllConfig["names"]["names"].extend(names)
    logger.info(f"✅ Added {len(names)} names.")
    return f"✅ {len(names)} نام جدید به لیست اضافه شد."


# -------------------------------
# ⏱ تنظیم فاصله زمانی تغییر
# -------------------------------
async def nm_set_interval(hours: int) -> str:
    """
    تعیین فاصله زمانی بین تغییر خودکار نام‌ها.
    """
    if hours <= 0:
        return "❌ مقدار زمان معتبر نیست."
    AllConfig["names"]["change_interval_h"] = hours
    logger.info(f"⏱ Interval set to {hours} hour(s).")
    return f"⏱ فاصله تغییر نام روی {hours} ساعت تنظیم شد."


# -------------------------------
# 🔁 فعال یا غیرفعال کردن تغییر خودکار
# -------------------------------
async def nm_toggle(enable: bool) -> str:
    """
    فعال یا غیرفعال کردن سیستم تغییر خودکار نام‌ها.
    """
    AllConfig["names"]["changenames"] = enable

    # اگر فعال شد
    if enable:
        if not AllConfig["names"]["names"]:
            return "❌ هیچ نامی برای تغییر وجود ندارد."

        if AllConfig["names"]["changenames_task"]:
            return "⚠️ فرآیند تغییر نام از قبل فعال است."

        AllConfig["names"]["changenames_task"] = asyncio.create_task(_change_name_loop())
        logger.info("🚀 Auto name changer started.")
        return "✅ تغییر خودکار نام‌ها فعال شد."

    # اگر غیرفعال شد
    task = AllConfig["names"].get("changenames_task")
    if task:
        try:
            task.cancel()
        except Exception:
            pass
        AllConfig["names"]["changenames_task"] = None
    logger.info("🛑 Auto name changer stopped.")
    return "🛑 تغییر خودکار نام‌ها غیرفعال شد."


# -------------------------------
# 🔄 حلقه تغییر خودکار نام‌ها
# -------------------------------
async def _change_name_loop():
    """
    حلقه پس‌زمینه برای تغییر خودکار نام‌ها با فواصل زمانی مشخص.
    """
    app = AllConfig["names"].get("app")
    if not app:
        logger.warning("⚠️ App instance not found for name changer.")
        return

    while AllConfig["names"].get("changenames", False):
        try:
            names = AllConfig["names"].get("names", [])
            if not names:
                await asyncio.sleep(30)
                continue

            idx = AllConfig["names"].get("changenames_idx", 0)
            new_name = names[idx % len(names)]

            await app.update_profile(first_name=new_name)
            logger.info(f"🪄 Changed name to: {new_name}")

            AllConfig["names"]["changenames_idx"] = (idx + 1) % len(names)
            interval = AllConfig["names"].get("change_interval_h", 1)
            await asyncio.sleep(interval * 3600)

        except asyncio.CancelledError:
            logger.info("🧹 Name change loop cancelled.")
            break
        except Exception as e:
            logger.error(f"⚠️ Error in name changer loop: {e}")
            await asyncio.sleep(15)


# -------------------------------
# 📊 وضعیت فعلی سیستم تغییر نام
# -------------------------------
async def nm_status() -> str:
    """
    نمایش وضعیت فعلی سیستم تغییر خودکار نام‌ها.
    """
    cfg = AllConfig["names"]
    names = cfg.get("names", [])
    if not names:
        return "⚠️ لیست نام‌ها خالی است."

    status = (
        "📋 **وضعیت تغییر خودکار نام‌ها:**\n"
        f"🔹 فعال: {'✅' if cfg.get('changenames', False) else '❌'}\n"
        f"🔹 فاصله تغییر: {cfg.get('change_interval_h', 1)} ساعت\n"
        f"🔹 تعداد نام‌ها: {len(names)}\n"
        f"🔹 اندیس فعلی: {cfg.get('changenames_idx', 0) + 1} از {len(names)}\n"
        f"🔹 نام در حال استفاده: {names[cfg.get('changenames_idx', 0) % len(names)]}"
    )
    return status
