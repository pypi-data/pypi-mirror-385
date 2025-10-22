# -*- coding: utf-8 -*-
# File: SBself/modules/text/text_manager_cmds.py
"""
مدیریت متن‌ها (لیست در کانفیگ) + مدیریت کپشن

- متن‌ها: در AllConfig["text"]["lines"] نگهداری می‌شوند.
- کپشن: در AllConfig["spammer"]["text_caption"] نگهداری می‌شود.

توابع async هستند و پیام آمادهٔ نمایش برمی‌گردانند.
"""

from __future__ import annotations
from typing import List
from SBself.config import AllConfig

# =============================
# 🧾 TEXT MANAGER (in-config storage)
# =============================

def _text_list() -> List[str]:
    """لیست متن‌ها را از کانفیگ برمی‌گرداند (و در صورت نبود ایجاد می‌کند)."""
    return AllConfig.setdefault("text", {}).setdefault("lines", [])

async def text_add_line(line: str) -> str:
    """افزودن یک خط به لیست متن‌ها."""
    line = (line or "").strip()
    if not line:
        return "❗ متن خالی است."
    L = _text_list()
    L.append(line)
    return f"✅ اضافه شد. تعداد کل: {len(L)}"

async def text_add_bulk(multiline: str) -> str:
    """افزودن چند خط (ورودی چندخطی). سطرهای خالی نادیده گرفته می‌شوند."""
    raw = (multiline or "").replace("\r", "")
    lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
    if not lines:
        return "❗ چیزی برای اضافه‌کردن پیدا نشد."
    L = _text_list()
    L.extend(lines)
    return f"✅ {len(lines)} خط اضافه شد. مجموع: {len(L)}"
async def set_full_text(text):
    L = _text_list()
    L.append(text)
    return f"{text} به لیست تکست ها اضافه شد"

async def text_del_line(line: str) -> str:
    """حذف دقیق یک خط از لیست متن‌ها (جستجوی برابر)."""
    line = (line or "").strip()
    if not line:
        return "❗ متن خالی است."
    L = _text_list()
    try:
        L.remove(line)
        return f"🗑️ حذف شد. باقی‌مانده: {len(L)}"
    except ValueError:
        return "⚠️ چنین خطی پیدا نشد."

async def text_clear_all() -> str:
    """پاک‌کردن همهٔ خطوط لیست متن‌ها."""
    L = _text_list()
    L.clear()
    return "🧹 همهٔ خطوط پاک شد."

async def text_get_all() -> str:
    """نمایش همهٔ خطوط به‌شکل فهرست شماره‌دار."""
    L = _text_list()
    if not L:
        return "ℹ️ لیست متن‌ها خالی است."
    body = "\n".join(f"{i+1}. {t}" for i, t in enumerate(L))
    return f"**لیست متن‌ها ({len(L)} مورد):**\n{body}"


# =============================
# 🏷 CAPTION MANAGER
# =============================

def _caption_ref() -> str:
    return AllConfig.setdefault("spammer", {}).setdefault("text_caption", "")

async def set_caption(text: str) -> str:
    """تنظیم کپشن پیش‌فرض در کانفیگ (spammer.text_caption)."""
    AllConfig.setdefault("spammer", {})["text_caption"] = text or ""
    return "✅ کپشن تنظیم شد."

async def clear_caption() -> str:
    """پاک‌کردن کپشن پیش‌فرض."""
    AllConfig.setdefault("spammer", {})["text_caption"] = ""
    return "🧹 کپشن پاک شد."

async def get_caption() -> str:
    """نمایش کپشن کنونی."""
    cap = AllConfig.setdefault("spammer", {}).get("text_caption", "") or ""
    return f"**Caption:**\n{cap}" if cap else "ℹ️ کپشن خالی است."


__all__ = [
    # text (in-config)
    "text_add_line", "text_add_bulk", "text_del_line", "text_clear_all", "text_get_all","set_full_text",
    # caption
    "set_caption", "clear_caption", "get_caption",
]
