# CliSelf/modules/chat_cleaner.py

import asyncio
from pyrogram import Client
from ...core.logger import get_logger

logger = get_logger("chat_cleaner")

class ChatCleaner:
    """
    ChatCleaner
    ------------
    ابزار حذف پیام‌ها از چت‌ها.
    شامل:
        - clear_all(): حذف کامل تمام پیام‌ها از چت
        - clear_last(): حذف آخرین N پیام
    """

    def __init__(self, client: Client):
        self.client = client
        logger.info("ChatCleaner initialized successfully.")

    async def clear_all(self, chat_id, title=None):
        done = 0
        try:
            logger.info(f"🧹 Starting full deletion for chat {chat_id} ({title or 'Unknown'})")
            async for m in self.client.iter_history(chat_id):
                try:
                    await self.client.delete_messages(chat_id, m.id, revoke=True)
                    done += 1
                    if done % 50 == 0:
                        logger.info(f"Progress: {done} messages deleted...")
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.warning(f"⚠️ Error deleting message {m.id}: {type(e).__name__}")
                    await asyncio.sleep(0.2)

            await self.client.send_message(
                "me",
                f"✅ DelAll Done\nChat: {title or chat_id}\nRemoved: {done}"
            )
            logger.info(f"✅ All messages deleted from chat {chat_id}. Count: {done}")
            return f"🧹 حذف کامل انجام شد ({done} پیام)."

        except Exception as e:
            logger.error(f"💥 Error during clear_all: {type(e).__name__} - {e}")
            raise

    async def clear_last(self, chat_id, n: int, current_msg_id: int = None):
        deleted = 0
        try:
            logger.info(f"🧹 Deleting last {n} messages from chat {chat_id}")
            async for m in self.client.iter_history(chat_id):
                if current_msg_id and m.id == current_msg_id:
                    continue
                try:
                    await self.client.delete_messages(chat_id, m.id, revoke=True)
                    deleted += 1
                    if deleted % 25 == 0:
                        logger.info(f"Progress: {deleted}/{n} messages deleted...")
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.warning(f"⚠️ Failed deleting message {m.id}: {type(e).__name__}")
                    await asyncio.sleep(0.2)
                if deleted >= n:
                    break

            logger.info(f"✅ Deleted {deleted} messages from chat {chat_id}")
            return f"🗑️ {deleted} پیام حذف شد."

        except Exception as e:
            logger.error(f"💥 Error during clear_last: {type(e).__name__} - {e}")
            raise
