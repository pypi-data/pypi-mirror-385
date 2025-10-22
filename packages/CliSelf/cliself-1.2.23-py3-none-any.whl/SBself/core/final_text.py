# -*- coding: utf-8 -*-
# File: SBself/core/final_text.py
#
# ماژولِ ساخت «متن نهایی» جهت ارسال در اسپمر
# - انتخاب متن تصادفی از AllConfig["text"]["lines"]
# - افزودن کپشن در صورت فعال بودن
# - افزودن منشن تکی و/یا گروهی (با لیبل textMen) به‌صورت HTML (tg://user?id=...)
#
# توجه:
#   * اسپمر باید پیام را با parse_mode="html" ارسال کند تا منشن‌ها درست رندر شوند.
#   * چیدمان منشن‌های گروهی مطابق ترتیب موجود در AllConfig["mention"]["group_ids"] خواهد بود.

from __future__ import annotations

import random
from typing import List, Optional

from ..config import AllConfig
from ..core.utils import make_mention_html  # سازنده‌ی <a href="tg://user?id=...">label</a>


# =========================
# متن تصادفی
# =========================
def get_random_text() -> str:
    """
    یک متن تصادفی از AllConfig["text"]["lines"] برمی‌گرداند.
    اگر لیست تهی باشد، رشته‌ی خالی می‌دهد.
    """
    lines = AllConfig.setdefault("text", {}).setdefault("lines", [])
    clean = [str(x).strip() for x in lines if str(x).strip()]
    return random.choice(clean) if clean else ""


# =========================
# کپشن
# =========================
def build_caption() -> str:
    """
    اگر در کانفیگ spammer یکی از حالت‌های زیر برقرار باشد، کپشن به خروجی افزوده می‌شود:
      - caption_on == True و متن caption خالی نباشد، یا
      - (برای سازگاری) caption خالی نباشد.
    خروجی به صورت "\n{caption}" است.
    """
    scfg = AllConfig.setdefault("spammer", {})
    caption = (scfg.get("text_caption") or "").strip()
    use_caption = bool(scfg.get("caption_on", False)) or bool(caption)
    return f"\n{caption}" if (use_caption and caption) else ""


# =========================
# منشن‌ها
# =========================
def _normalize_user_id(val) -> Optional[int]:
    """تبدیل ورودی به int (در صورت امکان). در غیر این صورت None."""
    try:
        return int(str(val).strip().lstrip("@"))
    except Exception:
        return None


def build_mentions() -> str:
    """
    ساخت رشته‌ی منشن‌ها بر اساس کانفیگ:
      - منشن تکی (is_menshen + useridMen + textMen)
      - منشن گروهی (group_menshen + group_ids) — همگی با لیبل textMen
    خروجی:
      - اگر چیزی برای افزودن نباشد: ""
      - در غیر این صورت: "\n" + " ".join(mentions)
    """
    mcfg = AllConfig.setdefault("mention", {})
    parts: List[str] = []

    # لیبل مشترک برای منشن‌ها
    label = (mcfg.get("textMen") or "mention").strip() or "mention"

    # --- منشن تکی
    if mcfg.get("is_menshen") and mcfg.get("useridMen"):
        uid = _normalize_user_id(mcfg.get("useridMen"))
        if uid:
            parts.append(make_mention_html(uid, label))

    # --- منشن گروهی (با حفظ ترتیب)
    if mcfg.get("group_menshen") and mcfg.get("group_ids"):
        for gid in mcfg.get("group_ids", []):
            g = _normalize_user_id(gid)
            if g:
                parts.append(make_mention_html(g, label))

    return ("\n" + " ".join(parts)) if parts else ""


# =========================
# مونتاژ نهایی
# =========================
def build_final_text(base: Optional[str] = None) -> str:
    """
    متن نهایی = متن پایه (base یا متن تصادفی) + کپشن (در صورت فعال بودن) + منشن‌ها
    اگر در نهایت چیزی برای ارسال نبود، رشته‌ی خالی برمی‌گرداند.
    """
    base_text = (base or "").strip() or get_random_text()
    if not base_text:
        return ""
    return "".join([base_text, build_caption(), build_mentions()])
