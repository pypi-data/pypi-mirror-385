# CliSelf/modules/forward_queue_manager.py

import os
import re
import json
import asyncio
import urllib.parse as up
from pyrogram import Client, errors
from ...core.logger import get_logger

logger = get_logger("forward_queue")


class ForwardQueueManager:
    """
    ForwardQueueManager
    --------------------
    مدیریت صف فوروارد پیام‌ها به تارگت‌های مشخص.
    قابلیت‌ها:
        - ذخیره لینک پیام‌ها (save_for_forward)
        - تنظیم تارگت‌ها (add_targets)
        - شروع فوروارد خودکار با تاخیر دلخواه (start_forward)
    """

    def __init__(self, client: Client, storage_path="data/forward_queue.json"):
        self.client = client
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self.data = {"messages": [], "targets": []}
        self._load()
        logger.info("ForwardQueueManager initialized successfully.")

    # ---------------------------------------------------------------
    # 📂 بارگذاری / ذخیره‌سازی داده‌ها
    # ---------------------------------------------------------------
    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                try:
                    self.data = json.load(f)
                except:
                    self.data = {"messages": [], "targets": []}
        else:
            self._save()

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------------------
    # 🔹 استخراج chat_id و message_id از لینک پیام
    # ---------------------------------------------------------------
    def _parse_message_link(self, link: str):
        """
        لینک‌های پشتیبانی‌شده:
          - https://t.me/c/123456789/10
          - https://t.me/username/22
        """
        link = link.strip()
        if "t.me/" not in link:
            raise ValueError("لینک پیام نامعتبر است.")

        parts = up.urlparse(link).path.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("لینک ناقص است.")

        chat_part, msg_part = parts[0], parts[1]
        if chat_part == "c":
            # فرمت t.me/c/<internal_id>/<msg_id>
            m = re.search(r"t\.me/c/(\d+)/(\d+)", link)
            if not m:
                raise ValueError("لینک t.me/c نامعتبر است.")
            chat_id = int(f"-100{m.group(1)}")
            msg_id = int(m.group(2))
        else:
            chat_id = chat_part
            msg_id = int(msg_part)

        return chat_id, msg_id

    # ---------------------------------------------------------------
    # 🔹 افزودن پیام به لیست فوروارد
    # ---------------------------------------------------------------
    async def save_message_for_forward(self, message_link: str):
        try:
            chat_id, msg_id = self._parse_message_link(message_link)
            entry = {"chat_id": chat_id, "msg_id": msg_id}
            if entry not in self.data["messages"]:
                self.data["messages"].append(entry)
                self._save()
                logger.info(f"✅ Saved message link {message_link}")
                return f"✅ پیام ذخیره شد ({chat_id}/{msg_id})"
            else:
                return "ℹ️ این پیام قبلاً ذخیره شده است."
        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            raise

    # ---------------------------------------------------------------
    # 🔹 افزودن تارگت‌ها
    # ---------------------------------------------------------------
    async def add_targets(self, *targets):
        new_targets = [t.strip() for t in targets if t.strip()]
        added = 0
        for t in new_targets:
            if t not in self.data["targets"]:
                self.data["targets"].append(t)
                added += 1
        self._save()
        logger.info(f"✅ Added {added} targets.")
        return f"✅ {added} مقصد جدید ثبت شد."

    # ---------------------------------------------------------------
    # 🔹 شروع فوروارد
    # ---------------------------------------------------------------
    async def start_forward(self, delay: int = 60):
        """
        تمام پیام‌های ذخیره‌شده را به تمام تارگت‌ها با تاخیر مشخص ارسال می‌کند.
        delay: فاصله بین ارسال‌ها بر حسب ثانیه
        """
        msgs = self.data.get("messages", [])
        tgts = self.data.get("targets", [])
        if not msgs:
            return "❌ لیست پیام‌ها خالی است."
        if not tgts:
            return "❌ لیست مقصدها خالی است."

        total_sent = 0
        logger.info(f"🚀 Starting forward queue | Delay={delay}s | Messages={len(msgs)} | Targets={len(tgts)}")

        for msg in msgs:
            chat_id = msg["chat_id"]
            msg_id = msg["msg_id"]
            for t in tgts:
                try:
                    await self.client.forward_messages(t, chat_id, msg_id)
                    total_sent += 1
                    logger.info(f"📤 Forwarded message {msg_id} → {t}")
                    await asyncio.sleep(delay)
                except errors.FloodWait as e:
                    logger.warning(f"⏰ FloodWait {e.value}s on forward to {t}")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to forward message {msg_id} to {t}: {type(e).__name__} - {e}")

        logger.info(f"✅ Forward complete. Total sent: {total_sent}")
        return f"✅ ارسال انجام شد ({total_sent} فوروارد)."

    # ---------------------------------------------------------------
    # 🔹 نمایش وضعیت
    # ---------------------------------------------------------------
    async def status(self):
        msgs = len(self.data.get("messages", []))
        tgts = len(self.data.get("targets", []))
        return f"🗂 پیام‌ها: {msgs}\n🎯 مقصدها: {tgts}"
