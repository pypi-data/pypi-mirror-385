# CliSelf/modules/forward_manager.py

import asyncio
import urllib.parse as up
from pyrogram import Client
from ...core.logger import get_logger

logger = get_logger("forward")

class ForwardManager:
    """
    ForwardManager
    ---------------
    مدیریت فوروارد پیام‌ها بین چت‌ها.
    شامل:
        - resolve_chat_id(): تشخیص و تبدیل ورودی (id, username, t.me link)
        - forward_all(): فوروارد تمام پیام‌ها از منبع به مقصد
    """

    def __init__(self, client: Client):
        self.client = client
        logger.info("ForwardManager initialized successfully.")

    # ----------------------------------------------------------
    # 🔹 تشخیص خودکار چت بر اساس ورودی (id, username, t.me link)
    # ----------------------------------------------------------
    async def resolve_chat_id(self, ident: str):
        """
        تشخیص و برگرداندن chat_id از انواع ورودی‌ها:
        - عددی (chat_id)
        - username یا لینک t.me
        - 'me' برای پیام به خود شخص
        """
        if not ident:
            return None
        ident = ident.strip()
        if ident.lower() == "me":
            return "me"

        if "t.me/" in ident:
            ident = up.urlparse(ident).path.strip("/")

        if ident.lstrip("-").isdigit():
            num = int(ident)
            try:
                c = await self.client.get_chat(num)
                return c.id
            except:
                try:
                    u = await self.client.get_users(num)
                    return u.id
                except:
                    return None

        try:
            c = await self.client.get_chat(ident)
            return c.id
        except:
            try:
                u = await self.client.get_users(ident)
                return u.id
            except:
                return None

    # ----------------------------------------------------------
    # 🔹 فوروارد تمام پیام‌ها از SRC به DEST
    # ----------------------------------------------------------
    async def forward_all(self, src: str, dst: str):
        """
        فوروارد تمام پیام‌ها از چت منبع (src) به چت مقصد (dst).
        پشتیبانی از ID، username، لینک t.me و 'me'.
        """
        src_id = await self.resolve_chat_id(src)
        dst_id = await self.resolve_chat_id(dst)

        if not src_id or not dst_id:
            logger.warning("SRC یا DEST نامعتبر است.")
            raise ValueError("SRC یا DEST نامعتبر است.")

        count = 0
        try:
            logger.info(f"🚀 Starting forward: {src} → {dst}")
            ids = []
            async for m in self.client.iter_history(src_id):
                ids.append(m.id)

            if not ids:
                logger.info("هیچ پیامی برای فوروارد وجود ندارد.")
                return "❌ پیامی برای فوروارد نیست."

            ids.reverse()  # تا از قدیمی به جدید فوروارد شود

            for i in range(0, len(ids), 100):
                chunk = ids[i:i + 100]
                try:
                    await self.client.forward_messages(dst_id, src_id, chunk)
                    count += len(chunk)
                    logger.info(f"✅ Forwarded {len(chunk)} messages ({count} total).")
                except Exception as e:
                    logger.warning(f"⚠️ Chunk forward failed: {type(e).__name__} - {e}")
                await asyncio.sleep(0.2)

            logger.info(f"✅ Forward complete: {count} messages from {src} → {dst}")
            return f"✅ {count} پیام از {src} به {dst} فوروارد شد."

        except Exception as e:
            logger.error(f"💥 Error during forward_all: {type(e).__name__} - {e}")
            raise
