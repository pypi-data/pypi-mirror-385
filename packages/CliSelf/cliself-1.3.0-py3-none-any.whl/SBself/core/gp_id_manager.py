# -*- coding: utf-8 -*-
# File: SBself/core/gp_id_manager.py
#
# ماژول واکشی و فرمت‌کردن اطلاعات چت (گروه/سوپرگروه/کانال/خصوصی)
# - تابع اصلی: fetch_group_info_text(client, chat_id) -> str (async)
# - تلاش می‌کند بیشترین اطلاعات ممکن را بر اساس نوع چت (Chat.type) برگرداند.
# - ایمن در برابر نبود برخی فیلدها (getattr + try/except).
# - شمارش اعضا با چند روش جایگزین (برای سازگاری نسخه‌ها).

from __future__ import annotations

from typing import Optional, Any, Dict

from pyrogram.enums import ChatType


def _yn(v: Optional[bool]) -> str:
    return "✅" if bool(v) else "❌"


def _fmt(val: Any) -> str:
    """نمایش دوستانه مقدارها؛ اگر None/خالی بود، «—»"""
    if val is None:
        return "—"
    if isinstance(val, str):
        s = val.strip()
        return s if s else "—"
    return str(val)


def _make_link(username: Optional[str]) -> str:
    if username:
        un = username.strip().lstrip("@")
        if un:
            return f"https://t.me/{un}"
    return "—"


async def _safe_members_count(client, chat_id: int) -> Optional[int]:
    """
    تلاش برای گرفتن تعداد اعضا در چند مسیر (بسته به نسخه Pyrogram/نوع چت).
    در صورت شکست، None برمی‌گرداند.
    """
    # تلاش 1: get_chat_members_count (برخی نسخه‌ها)
    fn = getattr(client, "get_chat_members_count", None)
    if callable(fn):
        try:
            return int(await fn(chat_id))
        except Exception:
            pass

    # تلاش 2: get_chat_member_count (نام مشابه در نسخه‌های جدیدتر)
    fn2 = getattr(client, "get_chat_member_count", None)
    if callable(fn2):
        try:
            return int(await fn2(chat_id))
        except Exception:
            pass

    # تلاش 3: get_chat و استفاده از .members_count اگر داشته باشد
    try:
        ch = await client.get_chat(chat_id)
        mc = getattr(ch, "members_count", None)
        if mc is not None:
            return int(mc)
    except Exception:
        pass

    return None


def _permissions_to_lines(perms: Optional[Any]) -> str:
    """
    تبدیل شیء permissions به خطوطی خوانا. اگر نبود یا از نوع غیرمنتظره بود، «—».
    """
    if perms is None:
        return "—"
    # تلاش برای استخراج attributeهای رایج
    keys = [
        "can_send_messages", "can_send_audios", "can_send_documents", "can_send_photos",
        "can_send_videos", "can_send_video_notes", "can_send_voice_notes",
        "can_send_polls", "can_send_other_messages",
        "can_add_web_page_previews",
        "can_change_info", "can_invite_users", "can_pin_messages",
        "can_manage_topics",
    ]
    lines = []
    for k in keys:
        v = getattr(perms, k, None)
        lines.append(f"• {k}: {_yn(v)}")
    # اگر هیچ‌کدام نبود، خروجی ساده
    if all("❌" in ln or "—" in ln for ln in lines):
        return "—"
    return "\n".join(lines)


async def fetch_group_info_text(client, chat_id: int) -> str:
    """
    اطلاعات چت را واکشی و به صورت متن آمادهٔ ارسال برمی‌گرداند.
    این تابع با پیام «/gp_id» در همان چتی که فراخوانی شود عالی کار می‌کند.
    """
    try:
        chat = await client.get_chat(chat_id)
    except Exception as e:
        return f"❌ خطا در واکشی اطلاعات چت: {e}"

    ctype = getattr(chat, "type", None)
    title = getattr(chat, "title", None)
    username = getattr(chat, "username", None)
    bio = getattr(chat, "bio", None)  # برای user/privates
    description = getattr(chat, "description", None)  # برای گروه/کانال
    is_verified = getattr(chat, "is_verified", None)
    is_scam = getattr(chat, "is_scam", None)
    is_fake = getattr(chat, "is_fake", None)
    is_restricted = getattr(chat, "is_restricted", None)
    dc_id = getattr(chat, "dc_id", None)
    slow_mode_delay = getattr(chat, "slow_mode_delay", None)
    linked_chat = getattr(chat, "linked_chat", None)  # ممکن است Chat یا None
    permissions = getattr(chat, "permissions", None)  # برای گروه‌ها
    has_protected_content = getattr(chat, "has_protected_content", None)
    # تعداد اعضا
    members_count = await _safe_members_count(client, chat_id)

    # لینک
    link = _make_link(username)

    # تشخیص نوع
    ctype_human = {
        ChatType.PRIVATE: "خصوصی",
        ChatType.BOT: "بات",
        ChatType.GROUP: "گروه",
        ChatType.SUPERGROUP: "سوپرگروه",
        ChatType.CHANNEL: "کانال",
    }.get(ctype, _fmt(ctype))

    # اگر لینک‌شده وجود داشته باشد، آیدی و عنوانش را استخراج کن
    linked_line = "—"
    try:
        if linked_chat is not None:
            lid = getattr(linked_chat, "id", None)
            ltitle = getattr(linked_chat, "title", None) or getattr(linked_chat, "first_name", None)
            linked_line = f"{_fmt(ltitle)} (`{_fmt(lid)}`)"
    except Exception:
        pass

    # مجوزها
    perms_text = _permissions_to_lines(permissions)

    # نام برای PRIVATE
    name_line = ""
    if ctype in (ChatType.PRIVATE, ChatType.BOT):
        first_name = getattr(chat, "first_name", None)
        last_name = getattr(chat, "last_name", None)
        full = " ".join([p for p in [first_name, last_name] if p]).strip()
        name_line = f"👤 نام: {_fmt(full)}\n"

    # بدنهٔ پیام
    parts = [
        "🧾 **اطلاعات چت**",
        f"🪪 آیدی: `{chat.id}`",
        f"🏷 عنوان: {_fmt(title)}",
        f"📣 نوع: {_fmt(ctype_human)}",
        f"🔗 لینک: {_fmt(link)}",
    ]

    if name_line:
        parts.append(name_line.rstrip())

    # توضیحات / بیو
    if ctype in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        parts.append(f"📝 توضیحات: {_fmt(description)}")
    else:
        parts.append(f"🧬 بیو: {_fmt(bio)}")

    # وضعیت‌ها
    parts.extend([
        f"✔️ وریفای‌شده: {_yn(is_verified)}",
        f"🚩 اسکَم: {_yn(is_scam)}",
        f"🎭 فِیک: {_yn(is_fake)}",
        f"⛔ محدود‌شده: {_yn(is_restricted)}",
        f"📦 محتوا محافظت‌شده: {_yn(has_protected_content)}",
    ])

    # مشخصات اضافی
    parts.extend([
        f"🧮 تعداد اعضا: {_fmt(members_count)}",
        f"⏱ Slow Mode: {_fmt(slow_mode_delay)} ثانیه" if slow_mode_delay else "⏱ Slow Mode: —",
        f"🔗 چت لینک‌شده: {linked_line}",
        f"🛂 مجوزهای پایه:\n{perms_text}",
        f"🌐 DC: {_fmt(dc_id)}",
    ])

    return "\n".join(parts)
