# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_manager.py

import asyncio
from typing import List, Union
from pyrogram import Client

class MultiForwarder:
    """
    MultiForwarder
    ---------------
    مدیریت فوروارد چند پیام (msg_ids) از یک سورس به چند تارگت.
    ویژگی‌ها:
      - افزودن پیام‌ها و تارگت‌ها
      - پشتیبانی از همه نوع پیام (forward)
      - شروع/توقف عملیات
      - تنظیم سرعت بین ارسال‌ها
    """

    def __init__(self, source_chat: Union[int, str]):
        self.source_chat = source_chat    # چت مبدا پیام‌ها (می‌تواند int یا username باشد)
        self.message_ids: List[int] = []  # لیست msg_id ها
        self.targets: List[Union[int, str]] = []  # لیست تارگت‌ها
        self.delay: int = 5               # پیش‌فرض هر 5 ثانیه
        self.is_running: bool = False
        self._task = None                 # برای کنترل task در asyncio

    # -----------------------------
    # افزودن / پاکسازی داده‌ها
    # -----------------------------
    def add_message(self, msg_id: int):
        """افزودن یک پیام به لیست فوروارد"""
        if msg_id not in self.message_ids:
            self.message_ids.append(msg_id)

    def add_target(self, chat_id: Union[int, str]):
        """افزودن یک تارگت جدید"""
        if chat_id not in self.targets:
            self.targets.append(chat_id)

    def clear_messages(self):
        self.message_ids.clear()

    def clear_targets(self):
        self.targets.clear()

    def set_delay(self, seconds: int):
        """تنظیم فاصله بین ارسال‌ها"""
        self.delay = max(1, seconds)

    # -----------------------------
    # عملیات اصلی
    # -----------------------------
    async def _forward_loop(self, client: Client):
        """حلقه فوروارد پیام‌ها به همه تارگت‌ها"""
        for mid in self.message_ids:
            for target in self.targets:
                if not self.is_running:
                    return
                try:
                    await client.forward_messages(
                        chat_id=target,
                        from_chat_id=self.source_chat,
                        message_ids=mid
                    )
                    await asyncio.sleep(self.delay)
                except Exception as e:
                    print(f"⚠️ خطا در فورواد msg {mid} به {target}: {e}")
        self.is_running = False

    async def start(self, client: Client):
        """شروع عملیات فوروارد"""
        if not self.message_ids:
            return "❌ هیچ پیام ثبت نشده."
        if not self.targets:
            return "❌ هیچ تارگتی ثبت نشده."

        if self.is_running:
            return "⚠️ عملیات از قبل در حال اجراست."

        self.is_running = True
        self._task = asyncio.create_task(self._forward_loop(client))
        return "🚀 عملیات فوروارد شروع شد."

    async def stop(self):
        """توقف عملیات"""
        if not self.is_running:
            return "⚠️ عملیات فعال نیست."
        self.is_running = False
        if self._task:
            self._task.cancel()
        return "🛑 عملیات متوقف شد."

    def status(self) -> str:
        """وضعیت فعلی عملیات"""
        return (
            "📊 **وضعیت MultiForwarder**\n"
            f"🔹 پیام‌ها: {len(self.message_ids)} عدد\n"
            f"🔹 تارگت‌ها: {len(self.targets)} عدد\n"
            f"⏱ سرعت: هر {self.delay} ثانیه\n"
            f"🚦 فعال: {'✅' if self.is_running else '❌'}"
        )
