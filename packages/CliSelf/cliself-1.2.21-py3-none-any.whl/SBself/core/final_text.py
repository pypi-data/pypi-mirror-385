# -*- coding: utf-8 -*-
# File: SBself/core/final_text.py
"""
final_text
-----------
ماژولی برای ساخت «متن نهایی» جهت اسپمر/ارسال‌های خودکار.

توابع:
- get_random_text(): یک متن تصادفی از AllConfig["text"]["lines"] برمی‌گرداند.
- build_caption(): اگر کپشن در کانفیگ روشن باشد، "\n{caption}" می‌سازد.
- build_mentions(): متن منشن‌ها (تکی/گروهی) را می‌سازد.
- build_final_text(base: Optional[str] = None): متن نهایی را از base (یا رندوم)
  + کپشن + منشن‌ها می‌سازد و برمی‌گرداند.
"""

from __future__ import annotations
from typing import List, Optional
import random
import html

from SBself.config import AllConfig
from SBself.core.utils import make_mention_html


# -----------------------------
# متن تصادفی
# -----------------------------
def get_random_text() -> str:
    """
    انتخاب یک متن به صورت تصادفی از AllConfig["text"]["lines"].
    اگر لیست خالی باشد، رشته‌ی خالی برمی‌گرداند.
    """
    lines = AllConfig.setdefault("text", {}).setdefault("lines", [])
    # حذف آیتم‌های خالی/فقط فاصله
    clean = [str(x).strip() for x in lines if str(x).strip()]
    return random.choice(clean) if clean else ""


# -----------------------------
# کپشن
# -----------------------------
def build_caption() -> str:
    """
    اگر در کانفیگ مقدار کپشن روشن باشد، "\n{caption}" برمی‌گرداند.
    معیار روشن بودن:
      - اگر AllConfig["spammer"]["caption_on"] == True باشد، یا
      - اگر کلید caption_on وجود نداشت ولی خود caption خالی نبود (سازگار با تنظیمات فعلی).
    """
    scfg = AllConfig.setdefault("text", {})
    caption = (scfg.get("caption") or "").strip()
    return f"\n{caption}"
# -----------------------------
# منشن
# -----------------------------
def build_mentions() -> str:
    """
    منشن تکی:
      - mention.is_menshen == True
      - mention.useridMen  (int/str)
      - mention.textMen    (متنِ لِیبِل)

    منشن گروهی (اختیاری):
      - mention.group_menshen == True
      - mention.group_ids = [user_id, ...]

    خروجی: رشته منشن‌ها با یک "\n" شروع می‌شود، اگر چیزی برای چسباندن باشد.
    """
    mcfg = AllConfig.setdefault("mention", {})
    parts: List[str] = []

    # تکی
    if mcfg.get("is_menshen") and mcfg.get("useridMen"):
        text_label = (mcfg.get("textMen") or "mention").strip() or "mention"
        try:
            uid = int(str(mcfg["useridMen"]).strip().lstrip("@"))
            parts.append(make_mention_html(uid, text_label))
        except Exception:
            pass

    # گروهی
    if mcfg.get("group_menshen") and mcfg.get("group_ids"):
        for gid in mcfg["group_ids"]:
            try:
                gid_int = int(str(gid).strip().lstrip("@"))
                parts.append(make_mention_html(gid_int, str(gid_int)))
            except Exception:
                continue

    return ("\n" + " ".join(parts)) if parts else ""


# -----------------------------
# مونتاژ نهایی
# -----------------------------
def build_final_text(base: Optional[str] = None) -> str:
    """
    base: متن پایه. اگر None یا خالی باشد از get_random_text() استفاده می‌شود.
    خروجی: base + caption + mentions
    """
    base = (base or "").strip() or get_random_text()
    if not base:
        return ""
    return "".join([base, build_caption(), build_mentions()])
