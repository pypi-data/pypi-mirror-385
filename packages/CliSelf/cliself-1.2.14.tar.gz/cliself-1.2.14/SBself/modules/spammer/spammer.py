# -*- coding: utf-8 -*-
# File: SBself/spammer/spammer.py

import asyncio 
from typing import List
from ...config import AllConfig
from ...core.utils import maybe_typing
def _compose_spam_text() -> str:
    """
    متن نهایی اسپم را از منابع زیر می‌سازد:
    - Text Manager:  AllConfig["text"]["fulltext"]  یا  join(AllConfig["text"]["lines"])
    - Caption:       AllConfig["spammer"]["text_caption"]  (به انتهای متن اضافه می‌شود)
    - Mention:       اگر mention_toggle روشن و useridMen ست باشد، در ابتدای متن می‌آید.
                     فرمت: [<textMen or 🔔>](tg://user?id=<userid>)
    """
    text_cfg   = AllConfig.setdefault("text", {})
    spam_cfg   = AllConfig.setdefault("spammer", {})
    mention_cfg= AllConfig.setdefault("mention", {})

    lines    = text_cfg.get("lines", []) or []
    fulltext = (text_cfg.get("fulltext") or "").strip()
    caption  = (spam_cfg.get("text_caption") or "").strip()

    men_on   = bool(mention_cfg.get("is_menshen"))
    men_uid  = str(mention_cfg.get("useridMen") or "").strip()
    men_txt  = (mention_cfg.get("textMen") or "").strip()

    # 1) پایه متن: fulltext اگر بود؛ وگرنه join(lines)
    base = fulltext if fulltext else ("\n".join(lines).strip() if lines else "")

    # 2) اگر کپشن هست، به انتهای متن اضافه شود
    if caption:
        base = f"{base}\n{caption}".strip() if base else caption

    # 3) اگر منشن روشن و uid ست بود، در ابتدای متن قرار بگیرد
    if men_on and men_uid:
        men = f"[{men_txt or '🔔'}](tg://user?id={men_uid})"
        base = f"{men}\n{base}".strip() if base else men

    # 4) اگر هیچ‌کدام نبود، یک متن حداقلی
    return base or "test"
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
                for chat_id in list(self.chat_ids):
                    try:
                        if AllConfig["spammer"]["typing_on"]:
                            await maybe_typing(self.app, chat_id, self.get_delay())
                            
                        text = _compose_spam_text()
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
