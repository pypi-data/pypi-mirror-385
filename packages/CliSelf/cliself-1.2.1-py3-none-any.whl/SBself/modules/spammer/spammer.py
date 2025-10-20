# -*- coding: utf-8 -*-
# File: SBself/spammer/spammer.py

import asyncio 
from typing import List
from ...config import AllConfig
from ...core.utils import maybe_typing, out


class Spammer:
    """
    کلاس مدیریت اسپمر (ارسال خودکار پیام‌ها به چت‌ها)
    """

    def __init__(self, app,chat_id):
        self.app = app
        self.chat_ids: List[int] = [chat_id]
        self.is_spamming: bool = False
        self.thread = None

    def get_delay(self) -> int:
        """دریافت فاصله زمانی از تنظیمات"""
        t = AllConfig["spammer"]["time"]
        try:
            return int(t)
        except Exception:
            return 5  

    async def run(self):
        """شروع اجرای اسپمر"""
        self.is_spamming = True
        while self.is_spamming:
            try:
                text = out(self.app)
                for chat_id in list(self.chat_ids):
                    try:
                        if AllConfig["spammer"]["typing_on"]:
                            await maybe_typing(self.app, chat_id, self.get_delay())

                        await self.app.send_message(chat_id, text)
                        await asyncio.sleep(self.get_delay())

                    except Exception as e:
                        print(f"[Spammer] Error sending to {chat_id}: {e}")

                # تأخیر بین تکرار پیام‌ها
                await asyncio.sleep(self.get_delay())

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Spammer] Loop error: {e}")
                await asyncio.sleep(5)
                
    def stop(self):
        """توقف اسپمر"""
        self.is_spamming = False
