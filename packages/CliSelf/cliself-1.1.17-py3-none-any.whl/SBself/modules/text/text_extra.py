# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/text_extra.py

import os
from pyrogram.types import Message
from ...config import AllConfig

# تلاش برای استفاده از logger اصلی پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("text_extra")
except Exception:
    import logging
    logger = logging.getLogger("text_extra")


async def gettext_file(message: Message = None) -> str:
    """
    ارسال فایل text.txt در صورت وجود.
    اگر message داده شود، مستقیماً فایل را برای همان چت ارسال می‌کند.
    اگر داده نشود، مسیر فایل را برمی‌گرداند.
    """

    text_path = "downloads/text.txt"

    # بررسی وجود فایل
    if not os.path.exists(text_path):
        logger.warning("❌ فایل text.txt یافت نشد.")
        if message:
            await message.reply("❌ فایل text.txt پیدا نشد.")
        return None

    # بررسی خالی نبودن فایل
    if os.path.getsize(text_path) == 0:
        logger.warning("⚠️ فایل text.txt خالی است.")
        if message:
            await message.reply("⚠️ فایل text.txt خالی است.")
        return None

    try:
        # ارسال فایل برای کاربر در صورت وجود message
        if message:
            await message.client.send_document(
                chat_id=message.chat.id,
                document=text_path,
                caption=AllConfig["spammer"].get("text_caption", "") or "📄 فایل متن‌ها"
            )
            await message.reply("✅ فایل ارسال شد.")
            logger.info(f"📤 فایل text.txt برای چت {message.chat.id} ارسال شد.")
        return text_path
    except Exception as e:
        logger.error(f"⚠️ خطا در ارسال فایل: {e}")
        if message:
            await message.reply(f"⚠️ خطا در ارسال فایل: {e}")
        return None
