# -*- coding: utf-8 -*-
# File: SBself/modules/mention/mention_manager.py
#
# مدیریت کامل منشن (تکی + گروهی) مطابق نیازمندی‌های شما
# - متن منشن: AllConfig["mention"]["textMen"]
# - منشن تکی: is_menshen + useridMen
# - منشن گروهی: group_menshen + group_ids (با حفظ ترتیب افزوده‌شدن)
# - افزودن جمعی ID ها (مانند: /mention_gps id1 id2 id3 ...)
# - افزودن از روی ریپلای
# - حذف یک یا چند ID
# - پاکسازی کامل لیست
# - گزارش وضعیت

from __future__ import annotations

from typing import Iterable, List, Tuple

from ...config import AllConfig

# تلاش برای استفاده از logger پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("mention_manager")
except Exception:
    import logging
    logger = logging.getLogger("mention_manager")


# -------------------------------
# 🧩 ابزارهای داخلی
# -------------------------------
def _ensure_cfg():
    """اطمینان از وجود ساختار کانفیگ mention و کلیدهای لازم."""
    m = AllConfig.setdefault("mention", {})
    m.setdefault("textMen", "")
    m.setdefault("useridMen", "")
    m.setdefault("is_menshen", False)
    m.setdefault("group_menshen", False)
    m.setdefault("group_ids", [])


def _normalize_id_token(tok: str) -> int | None:
    """
    نرمال‌سازی ورودی ID:
      - اعداد (مثبت/منفی) → همان int
      - '@username' یا 't.me/...' قابل تبدیل به ID عددی نیستند اینجا (مدیریت در لایه‌ی commands).
    """
    if tok is None:
        return None
    t = str(tok).strip()
    # فقط عدد را می‌پذیریم ( -100... هم مجاز )
    if t and (t.lstrip("-").isdigit()):
        try:
            return int(t)
        except Exception:
            return None
    return None


def _add_many_preserve_order(dst: List[int], ids: Iterable[int]) -> Tuple[int, int]:
    """
    افزودن چند ID با حفظ ترتیب و جلوگیری از تکرار.
    خروجی: (added_count, skipped_count)
    """
    added = 0
    skipped = 0
    exist = set(dst)
    for i in ids:
        try:
            ii = int(i)
        except Exception:
            skipped += 1
            continue
        if ii in exist:
            skipped += 1
            continue
        dst.append(ii)
        exist.add(ii)
        added += 1
    return added, skipped


def _remove_many(dst: List[int], ids: Iterable[int]) -> Tuple[int, int]:
    """
    حذف یک/چند ID از لیست. اگر نبود، شمرده می‌شود به عنوان skipped.
    خروجی: (removed_count, skipped_count)
    """
    removed = 0
    skipped = 0
    s = set(dst)
    for i in ids:
        try:
            ii = int(i)
        except Exception:
            skipped += 1
            continue
        if ii in s:
            # حذف تمام رخدادها (به‌صورت ایمن)
            dst[:] = [x for x in dst if x != ii]
            s.discard(ii)
            removed += 1
        else:
            skipped += 1
    return removed, skipped


# -------------------------------
# ✍️ تنظیم متن منشن
# -------------------------------
async def set_mention_text(text: str) -> str:
    _ensure_cfg()
    if not (text or "").strip():
        return "❌ متن منشن نمی‌تواند خالی باشد."
    AllConfig["mention"]["textMen"] = text.strip()
    logger.info(f"✅ Mention text set: {text.strip()}")
    return "✅ متن منشن تنظیم شد."


# -------------------------------
# 🆔 تنظیم شناسه کاربر برای منشن «تکی»
# -------------------------------
async def set_mention_user(user_id: int) -> str:
    _ensure_cfg()
    try:
        uid = int(user_id)
    except Exception:
        return "❌ شناسه کاربر معتبر نیست."
    AllConfig["mention"]["useridMen"] = uid
    logger.info(f"✅ Mention target set: {uid}")
    return f"✅ کاربر {uid} برای منشن تنظیم شد."


# -------------------------------
# ⚙️ فعال / غیرفعال کردن منشن «تکی»
# -------------------------------
async def toggle_mention(enable: bool) -> str:
    _ensure_cfg()
    AllConfig["mention"]["is_menshen"] = bool(enable)
    logger.info(f"🔄 Single mention {'enabled' if enable else 'disabled'}.")
    return "✅ منشن تکی فعال شد." if enable else "🛑 منشن تکی غیرفعال شد."


# -------------------------------
# 🔁 فعال / غیرفعال کردن منشن «گروهی»
# -------------------------------
async def toggle_group_mention(enable: bool) -> str:
    _ensure_cfg()
    AllConfig["mention"]["group_menshen"] = bool(enable)
    logger.info(f"🔄 Group mention {'enabled' if enable else 'disabled'}.")
    return "✅ منشن گروهی فعال شد." if enable else "🛑 منشن گروهی غیرفعال شد."


# -------------------------------
# 👥 افزودن گروه‌ها (چند ID یکجا)
#   مثال: /mention_gps id1 id2 id3 ...
#   نکته: اینجا فقط ID عددی را می‌پذیریم؛ ریـزولوشن username در لایه‌ی command انجام شود.
# -------------------------------
async def add_groups_by_ids(*ids: int | str) -> str:
    _ensure_cfg()
    groups: List[int] = AllConfig["mention"]["group_ids"]

    # نرمال‌سازی فقط IDهای عددی
    norm = []
    for t in ids:
        n = _normalize_id_token(str(t))
        if n is not None:
            norm.append(n)

    if not norm:
        return "❌ هیچ شناسهٔ معتبری دریافت نشد."

    added, skipped = _add_many_preserve_order(groups, norm)
    logger.info(f"✅ Group IDs added: +{added} / skipped:{skipped} → total:{len(groups)}")
    if added and not AllConfig["mention"].get("group_menshen", False):
        # اگر کاربر گروهی را روشن نکرده باشد، راهنمایی کوچکی بدهیم (اختیاری)
        return f"✅ {added} شناسه افزوده شد. ℹ️ برای استفاده، منشن گروهی را فعال کنید."
    return f"✅ {added} شناسه افزوده شد. {'(برخی تکراری/نامعتبر بودند.)' if skipped else ''}".strip()


# -------------------------------
# 📥 افزودن از روی ریپلای
#   (ID کاربر ریپلای‌شده را به لیست group_ids اضافه می‌کند)
# -------------------------------
async def add_group_from_reply(user_id: int) -> str:
    _ensure_cfg()
    try:
        uid = int(user_id)
    except Exception:
        return "❌ شناسهٔ ریپلای معتبر نیست."

    groups: List[int] = AllConfig["mention"]["group_ids"]
    added, skipped = _add_many_preserve_order(groups, [uid])
    logger.info(f"✅ Group add from reply: +{added} (uid={uid}) → total:{len(groups)}")
    return "✅ شناسهٔ کاربرِ ریپلای به لیست منشن گروهی اضافه شد." if added else "ℹ️ این شناسه قبلاً در لیست بود."


# -------------------------------
# ❌ حذف یک یا چند ID از group_ids
#   مثال: /mention_del id1 id2 ...
# -------------------------------
async def remove_groups_by_ids(*ids: int | str) -> str:
    _ensure_cfg()
    groups: List[int] = AllConfig["mention"]["group_ids"]

    norm = []
    for t in ids:
        n = _normalize_id_token(str(t))
        if n is not None:
            norm.append(n)

    if not norm:
        return "❌ هیچ شناسهٔ معتبری برای حذف دریافت نشد."

    removed, skipped = _remove_many(groups, norm)
    logger.info(f"🗑️ Group IDs removed: -{removed} / skipped:{skipped} → total:{len(groups)}")
    if removed:
        if skipped:
            return f"🗑️ {removed} شناسه حذف شد. (برخی یافت نشدند.)"
        return f"🗑️ {removed} شناسه حذف شد."
    return "ℹ️ هیچ‌کدام از شناسه‌ها در لیست نبود."


# -------------------------------
# 🧹 پاکسازی کامل گروه‌های منشن
# -------------------------------
async def clear_groups() -> str:
    _ensure_cfg()
    AllConfig["mention"]["group_ids"] = []
    logger.info("🧹 All group mention IDs cleared.")
    return "🧹 تمام گروه‌های منشن پاک شدند."


# -------------------------------
# 📊 وضعیت فعلی منشن
# -------------------------------
async def mention_status() -> str:
    _ensure_cfg()
    mention_cfg = AllConfig["mention"]
    text = mention_cfg.get("textMen", "")
    user_id = mention_cfg.get("useridMen", "")
    single_enabled = bool(mention_cfg.get("is_menshen", False))
    group_enabled = bool(mention_cfg.get("group_menshen", False))
    groups = list(mention_cfg.get("group_ids", []))

    msg = (
        "📋 **وضعیت منشن:**\n"
        f"💬 متن منشن: {text or '—'}\n"
        f"🎯 کاربر تکی: `{user_id or '—'}` — {'✅' if single_enabled else '❌'}\n"
        f"👥 گروهی فعال: {'✅' if group_enabled else '❌'}\n"
        f"📦 تعداد شناسه‌های گروهی: {len(groups)}\n"
    )

    if groups:
        msg += "\n🗂 **لیست گروهی (به ترتیب):**\n"
        msg += "\n".join([f"{i+1}. `{gid}`" for i, gid in enumerate(groups)])

    logger.info("📊 Mention status displayed.")
    return msg
