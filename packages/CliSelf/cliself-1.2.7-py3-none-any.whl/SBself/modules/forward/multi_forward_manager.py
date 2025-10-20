# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_manager.py

import asyncio
from typing import List, Union, Dict, Any
from pyrogram import Client

class MultiForwarder:
    """
    MultiForwarder (forward-only)
    -----------------------------
    فقط فوروارد می‌کند (بدون هیچ fallback به copy).
    تا وقتی stop نشود، در یک حلقه‌ی بی‌نهایت با delay مشخص، همه آیتم‌ها را
    به همه تارگت‌ها می‌فرستد و دوباره از اول تکرار می‌کند.
    
    هر آیتم:
      {
        "forward_chat_id": int|str,
        "forward_message_id": int
      }
    """

    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.targets: List[Union[int, str]] = []
        self.delay: int = 5
        self.is_running: bool = False
        self._task = None
        self._cycle_delay: int = 1  # فاصله بین دو دور کامل

    # ---------- Manage items & targets ----------
    def add_item(self, forward_chat_id: Union[int, str], forward_message_id: int):
        self.items.append({
            "forward_chat_id": forward_chat_id,
            "forward_message_id": forward_message_id
        })

    def clear_items(self):
        self.items.clear()

    def add_target(self, chat_id: Union[int, str]):
        if chat_id not in self.targets:
            self.targets.append(chat_id)

    def clear_targets(self):
        self.targets.clear()

    def set_delay(self, seconds: int):
        self.delay = max(1, int(seconds))

    def set_cycle_delay(self, seconds: int):
        """فاصله‌ی استراحت بین اتمام یک دور کامل و شروع دور بعدی"""
        self._cycle_delay = max(0, int(seconds))

    # ---------- Internal ----------
    async def _forward_once(self, client: Client, item: Dict[str, Any], target: Union[int, str]):
        try:
            await client.forward_messages(
                chat_id=target,
                from_chat_id=item["forward_chat_id"],
                message_ids=item["forward_message_id"]
            )
        except Exception as e:
            # فقط لاگ نرم و ادامه
            print(f"⚠️ forward error mid={item['forward_message_id']} -> {target}: {e}")

    async def _loop(self, client: Client):
        # حلقه بی‌نهایت تا stop
        while self.is_running:
            # اگر آیتم یا تارگت خالی شد، کمی صبر کن و دوباره چک کن
            if not self.items or not self.targets:
                await asyncio.sleep(1)
                continue

            for item in self.items:
                if not self.is_running:
                    break
                for tgt in self.targets:
                    if not self.is_running:
                        break
                    await self._forward_once(client, item, tgt)
                    await asyncio.sleep(self.delay)

            # پایان یک دور کامل
            if self._cycle_delay > 0 and self.is_running:
                await asyncio.sleep(self._cycle_delay)

        self.is_running = False

    # ---------- Public API ----------
    async def start(self, client: Client) -> str:
        if not self.items:
            return "❌ هیچ پیام فورواردی ثبت نشده."
        if not self.targets:
            return "❌ هیچ تارگتی ثبت نشده."
        if self.is_running:
            return "⚠️ عملیات از قبل در حال اجراست."

        self.is_running = True
        self._task = asyncio.create_task(self._loop(client))
        return "🚀 عملیات فوروارد (حلقه‌ای) شروع شد."

    async def stop(self) -> str:
        if not self.is_running:
            return "⚠️ عملیات فعال نیست."
        self.is_running = False
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass
        return "🛑 عملیات متوقف شد."

    def status(self) -> str:
        return (
            "📊 **وضعیت MultiForwarder**\n"
            f"🔹 آیتم‌ها: {len(self.items)}\n"
            f"🔹 تارگت‌ها: {len(self.targets)}\n"
            f"⏱ فاصله ارسال: {self.delay} ثانیه\n"
            f"🔁 فاصله بین دورها: {self._cycle_delay} ثانیه\n"
            f"🚦 فعال: {'✅' if self.is_running else '❌'}"
        )
