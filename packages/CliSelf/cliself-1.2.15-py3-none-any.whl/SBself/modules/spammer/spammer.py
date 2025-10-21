# -*- coding: utf-8 -*-
# File: SBself/spammer/spammer.py

import asyncio 
from typing import List
from ...config import AllConfig
from ...core.utils import maybe_typing
import html
from SBself.config import AllConfig

def _next_line_round_robin() -> str:
    """
    یک خط از AllConfig['text']['lines'] به صورت راند-رابین برمی‌گرداند
    و ایندکس را برای نوبت بعدی جلو می‌برد.
    """
    tcfg = AllConfig.setdefault("text", {})
    lines = tcfg.get("lines", []) or []
    if not lines:
        return ""  # یعنی از fulltext یا caption استفاده می‌کنیم
    idx = int(tcfg.get("lines_idx", 0)) % len(lines)
    tcfg["lines_idx"] = (idx + 1) % len(lines)
    return str(lines[idx]).strip()

def _compose_spam_text() -> str:
    """
    متن نهایی اسپم را می‌سازد:
    - اگر lines داشتیم، هر بار یکی از آن‌ها؛ وگرنه از fulltext استفاده می‌شود.
    - caption (در spammer_config['text_caption']) به انتهای متن اضافه می‌شود.
    - اگر منشن روشن بود، در ابتدای متن قرار می‌گیرد (Markdown).
    """
    tcfg   = AllConfig.setdefault("text", {})
    scfg   = AllConfig.setdefault("spammer", {})
    mcfg   = AllConfig.setdefault("mention", {})

    # 1) پایه متن: راند-رابین از lines، اگر نبود از fulltext
    base = _next_line_round_robin()
    if not base:
        base = (tcfg.get("fulltext") or "").strip()

    # 2) کپشن
    caption = (scfg.get("text_caption") or "").strip()
    if caption:
        base = f"{base}\n{caption}".strip() if base else caption

    # 3) منشن
    if mcfg.get("is_menshen") and str(mcfg.get("useridMen") or "").strip():
        uid = str(mcfg.get("useridMen")).strip()
        mtxt = (mcfg.get("textMen") or "🔔").strip()
        mention = f"[{mtxt}](tg://user?id={uid})"
        base = f"{mention}\n{base}".strip() if base else mention

    return base or "test"  # حداقل چیزی بفرستیم

def _compose_spam_text_html() -> str:
    """
    نسخه HTML-safe اگر ترجیح می‌دهی از parse_mode='html' استفاده کنی.
    """
    tcfg   = AllConfig.setdefault("text", {})
    scfg   = AllConfig.setdefault("spammer", {})
    mcfg   = AllConfig.setdefault("mention", {})

    base_line = _next_line_round_robin()
    base = base_line if base_line else (tcfg.get("fulltext") or "").strip()
    caption = (scfg.get("text_caption") or "").strip()

    if caption:
        base = f"{base}\n{caption}".strip() if base else caption

    if mcfg.get("is_menshen") and str(mcfg.get("useridMen") or "").strip():
        uid = str(mcfg.get("useridMen")).strip()
        mtxt = html.escape(mcfg.get("textMen") or "🔔")
        mention = f'<a href="tg://user?id={html.escape(uid)}">{mtxt}</a>'
        base = f"{mention}\n{html.escape(base)}".strip() if base else mention
    else:
        base = html.escape(base)

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
                            
                        text = _compose_spam_text_html()
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
