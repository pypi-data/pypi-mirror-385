# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward/multi_forward_manager.py

import asyncio
from typing import List, Optional, Union, Dict, Any
from pyrogram import Client

class MultiForwarder:
    """
    MultiForwarder
    ---------------
    نگهداری لیستی از آیتم‌ها برای فوروارد/کپی:
      هر آیتم می‌تواند منبع اصلی فوروارد داشته باشد (forward_from)
      یا نسخه‌ی محلی برای کپی (local_copy).

    ساختار هر آیتم:
      {
        "mode": "forward" | "copy",
        "forward_chat_id": Optional[int|str],
        "forward_message_id": Optional[int],
        "local_chat_id": Optional[int|str],
        "local_message_id": Optional[int],
      }
    """

    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.targets: List[Union[int, str]] = []
        self.delay: int = 5
        self.is_running: bool = False
        self._task = None

    # --------------- Manage items & targets ---------------
    def add_item(
        self,
        mode: str,
        forward_chat_id: Optional[Union[int, str]] = None,
        forward_message_id: Optional[int] = None,
        local_chat_id: Optional[Union[int, str]] = None,
        local_message_id: Optional[int] = None,
    ):
        item = {
            "mode": mode,
            "forward_chat_id": forward_chat_id,
            "forward_message_id": forward_message_id,
            "local_chat_id": local_chat_id,
            "local_message_id": local_message_id,
        }
        self.items.append(item)

    def clear_items(self):
        self.items.clear()

    def add_target(self, chat_id: Union[int, str]):
        if chat_id not in self.targets:
            self.targets.append(chat_id)

    def clear_targets(self):
        self.targets.clear()

    def set_delay(self, seconds: int):
        self.delay = max(1, int(seconds))

    # --------------- Internal helpers ---------------
    async def _try_forward(self, client: Client, item: Dict[str, Any], target: Union[int, str]) -> bool:
        """
        تلاش برای فوروارد؛ اگر خطای قابل‌پیش‌بینی بود، False تا مسیر fallback فعال شود.
        """
        try:
            await client.forward_messages(
                chat_id=target,
                from_chat_id=item["forward_chat_id"],
                message_ids=item["forward_message_id"]
            )
            return True
        except Exception as e:
            # خطاهای رایج: MESSAGE_ID_INVALID، CHAT_FORWARDS_FORBIDDEN، PEER_ID_INVALID
            err = str(e).upper()
            if (
                "MESSAGE_ID_INVALID" in err
                or "CHAT_FORWARDS_FORBIDDEN" in err
                or "FORWARDS_RESTRICTED" in err
                or "PEER_ID_INVALID" in err
            ):
                # اجازه بده fallback اجرا شود
                return False
            # سایر خطاها را هم به‌عنوان شکست فوروارد در نظر می‌گیریم تا fallback امتحان شود
            return False

    async def _try_copy(self, client: Client, item: Dict[str, Any], target: Union[int, str]) -> bool:
        """
        تلاش برای کپی از نسخه محلی.
        """
        try:
            await client.copy_message(
                chat_id=target,
                from_chat_id=item["local_chat_id"],
                message_id=item["local_message_id"]
            )
            return True
        except Exception:
            return False

    async def _send_item_to_target(self, client: Client, item: Dict[str, Any], target: Union[int, str]):
        """
        ارسال یک آیتم به یک تارگت با منطق fallback:
          - اگر forward داده شده بود: اول forward، در صورت خطا: copy (اگر local وجود داشت)
          - اگر فقط copy بود: مستقیماً copy
        """
        if item["mode"] == "forward":
            ok = await self._try_forward(client, item, target)
            if ok:
                return
            # fallback به کپی اگر نسخه‌ی محلی داریم
            if item.get("local_chat_id") and item.get("local_message_id"):
                await self._try_copy(client, item, target)
        else:
            # فقط کپی
            await self._try_copy(client, item, target)

    async def _loop(self, client: Client):
        for idx, item in enumerate(self.items, 1):
            if not self.is_running:
                break
            for tgt in self.targets:
                if not self.is_running:
                    break
                await self._send_item_to_target(client, item, tgt)
                await asyncio.sleep(self.delay)
        self.is_running = False

    # --------------- Public API ---------------
    async def start(self, client: Client) -> str:
        if not self.items:
            return "❌ هیچ پیامی ثبت نشده."
        if not self.targets:
            return "❌ هیچ تارگتی ثبت نشده."
        if self.is_running:
            return "⚠️ عملیات از قبل در حال اجراست."

        self.is_running = True
        self._task = asyncio.create_task(self._loop(client))
        return "🚀 عملیات فوروارد شروع شد."

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
            f"⏱ فاصله: {self.delay} ثانیه\n"
            f"🚦 فعال: {'✅' if self.is_running else '❌'}"
        )
