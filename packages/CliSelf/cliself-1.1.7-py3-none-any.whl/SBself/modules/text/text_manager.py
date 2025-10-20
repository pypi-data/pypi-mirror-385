# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/text_manager.py

import os
from ...config import AllConfig

# تلاش برای استفاده از logger پروژه؛ در صورت نبود، از logging استاندارد استفاده می‌کند
try:
    from ...core.logger import get_logger
    logger = get_logger("text")
except Exception:
    import logging
    logger = logging.getLogger("text")


class TextManager:
    """
    TextManager
    ------------
    مدیریت فایل متنی برای ذخیره، حذف و پاک‌سازی خطوط
    و همچنین مدیریت کپشن (caption).
    """

    def __init__(self, text_path: str = "downloads/text.txt"):
        self.text_path = text_path
        os.makedirs(os.path.dirname(self.text_path), exist_ok=True)
        if not os.path.exists(self.text_path):
            open(self.text_path, "w", encoding="utf-8").close()
        logger.info(f"✅ TextManager initialized at {self.text_path}")

    # -------------------------------
    # افزودن یک خط جدید
    # -------------------------------
    async def add_text(self, text: str) -> str:
        if not text.strip():
            logger.warning("Attempted to add empty text.")
            return "❌ متنی وارد نشده."
        with open(self.text_path, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        logger.info(f"✅ Added line: {text.strip()}")
        return "✅ متن ذخیره شد."

    # -------------------------------
    # افزودن چند خط به صورت یکجا
    # -------------------------------
    async def add_all_text(self, text_block: str) -> str:
        lines = [ln.strip() for ln in text_block.splitlines() if ln.strip()]
        if not lines:
            logger.warning("Attempted to add empty multi-line text block.")
            return "❌ متنی برای ذخیره وجود ندارد."
        with open(self.text_path, "a", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in lines)
        logger.info(f"✅ Added {len(lines)} lines.")
        return f"✅ {len(lines)} خط ذخیره شد."

    # -------------------------------
    # حذف خط مشخص از فایل
    # -------------------------------
    async def delete_text(self, target: str) -> str:
        if not target.strip():
            logger.warning("Attempted to delete empty target.")
            return "❌ متنی برای حذف وارد نشده."
        with open(self.text_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines()]
        kept = [ln for ln in lines if ln.strip() != target.strip()]
        removed = len(lines) - len(kept)
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write("\n".join(kept) + ("\n" if kept else ""))
        logger.info(f"🗑️ Deleted {removed} line(s) matching '{target.strip()}'")
        return f"🗑️ {removed} خط حذف شد."

    # -------------------------------
    # پاکسازی کل فایل متن
    # -------------------------------
    async def clear_text(self) -> str:
        open(self.text_path, "w", encoding="utf-8").close()
        logger.info("🧹 Cleared all text lines.")
        return "🧹 تمام خطوط متن حذف شد."

    # -------------------------------
    # تنظیم کپشن
    # -------------------------------
    async def set_caption(self, caption: str) -> str:
        if not caption.strip():
            logger.warning("Attempted to set empty caption.")
            return "❌ کپشن خالی است."
        AllConfig["spammer"]["text_caption"] = caption.strip()
        logger.info(f"📝 Caption set: {caption.strip()}")
        return "📝 کپشن ذخیره شد."

    # -------------------------------
    # پاکسازی کپشن
    # -------------------------------
    async def clear_caption(self) -> str:
        AllConfig["spammer"]["text_caption"] = ""
        logger.info("🧹 Caption cleared.")
        return "🧹 کپشن پاکسازی شد."

    # -------------------------------
    # گرفتن کپشن فعلی
    # -------------------------------
    async def get_caption(self) -> str:
        cap = AllConfig["spammer"].get("text_caption", "")
        return f"📄 کپشن فعلی:\n{cap if cap else '❌ کپشنی تنظیم نشده.'}"
