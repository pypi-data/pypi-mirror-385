# -*- coding: utf-8 -*-
# File: SBself/core/utils.py
"""
ابزارهای عمومی پروژه:

- متن‌ها از AllConfig["text"]["lines"] خوانده می‌شوند (نه فایل).
- کپشن از AllConfig["spammer"]["text_caption"].
- وضعیت typing از AllConfig["spammer"]["typing_on"].
- منشن‌ها از AllConfig["mention"] (is_menshen, useridMen, textMen, group_menshen, group_ids).
"""

from __future__ import annotations

import asyncio
import html
import random
import time
from typing import List, Optional

from SBself.config import AllConfig


# =============================
# 🧱 متن‌ها (from config, not file)
# =============================

def _text_lines() -> List[str]:
    """لیست متن‌ها از کانفیگ. در صورت نبود، ساخته می‌شود."""
    return AllConfig.setdefault("text", {}).setdefault("lines", [])


def pick_text() -> Optional[str]:
    """یک خط تصادفی از لیست متن‌ها برمی‌گرداند؛ اگر لیست خالی باشد None."""
    lines = [ln for ln in _text_lines() if ln and ln.strip()]
    if not lines:
        return None
    return random.choice(lines).strip()


# =============================
# 🔗 ساخت لینک‌ها و منشن‌ها
# =============================

def make_mention_html(user_id: int, text: str) -> str:
    """ساخت منشن HTML تلگرام به یک کاربر."""
    return f'<a href="tg://user?id={int(user_id)}">{html.escape(text or str(user_id))}</a>'


def chat_link_html(chat) -> str:
    """لینک HTML برای چت/گروه (اگر یوزرنیم داشته باشد)."""
    title = (getattr(chat, "title", "") or "").strip()
    username = getattr(chat, "username", None)
    if username:
        return f'<a href="https://t.me/{username}">{html.escape(title or username)}</a>'
    return html.escape(title or str(getattr(chat, "id", "")))


# =============================
# ⌨️ شبیه‌سازی تایپ کردن
# =============================

async def maybe_typing(client, chat_id: int, seconds: int = 2) -> None:
    """اگر typing_on فعّال باشد، برای چند ثانیه اکشن 'typing' ارسال می‌کند."""
    typing_on = AllConfig.setdefault("spammer", {}).get("typing_on", False)
    if not typing_on:
        return
    end = time.time() + max(1, int(seconds))
    while time.time() < end:
        try:
            await client.send_chat_action(chat_id, "typing")
        except Exception:
            pass
        await asyncio.sleep(3)


# =============================
# 🧩 ساخت متن نهایی (base + caption + mentions)
# =============================

def _caption_text() -> str:
    """کپشن پیش‌فرض از کانفیگ اسپمر."""
    return AllConfig.setdefault("spammer", {}).get("text_caption", "") or ""


def _mention_config() -> dict:
    """برگشت دیکشنری mention از کانفیگ با مقادیر پیش‌فرض امن."""
    return AllConfig.setdefault("mention", {
        "textMen": "",
        "useridMen": "",
        "is_menshen": False,
        "group_menshen": False,
        "group_ids": [],
    })


def build_full_text(base_text: str) -> str:
    """
    ترکیب متن پایه با کپشن و منشن‌ها.
    - اگر caption خالی نباشد با یک خط جدید اضافه می‌شود.
    - اگر منشن تکی فعّال باشد، منشن به انتها افزوده می‌شود.
    - اگر منشن گروهی فعّال باشد، منشن همهٔ IDها پشت‌هم اضافه می‌شود.
    """
    chunks: List[str] = []
    base = (base_text or "").strip()
    if base:
        chunks.append(base)

    cap = _caption_text().strip()
    if cap:
        chunks.append(cap)

    men_cfg = _mention_config()

    # منشن تکی
    if men_cfg.get("is_menshen") and men_cfg.get("useridMen"):
        try:
            uid = int(men_cfg["useridMen"])
            label = (men_cfg.get("textMen") or "mention").strip() or "mention"
            chunks.append(make_mention_html(uid, label))
        except Exception:
            # اگر تبدیل id به int شکست خورد، نادیده بگیر
            pass

    # منشن گروهی
    if men_cfg.get("group_menshen") and men_cfg.get("group_ids"):
        ids = []
        try:
            ids = [int(x) for x in men_cfg["group_ids"] if str(x).strip()]
        except Exception:
            # اگر یکی خراب بود، فقط سالم‌ها را در نظر می‌گیریم
            ids = [int(x) for x in men_cfg.get("group_ids", []) if str(x).isdigit()]
        if ids:
            group_mentions = " ".join(make_mention_html(uid, str(uid)) for uid in ids)
            chunks.append(group_mentions)

    return "\n".join(chunks).strip()


# =============================
# 🎯 خروجی نهایی برای ارسال
# =============================

def out_text() -> Optional[str]:
    """
    انتخاب یک متن تصادفی از لیست و افزودن کپشن/منشن.
    اگر لیست خالی باشد، None.
    """
    base = pick_text()
    if base is None:
        return None
    return build_full_text(base)
