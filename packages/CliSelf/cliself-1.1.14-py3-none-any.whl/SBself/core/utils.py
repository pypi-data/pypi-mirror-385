# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/utils.py

import time, asyncio, html, random
from ..config import AllConfig
import urllib.parse as up


# -----------------------------
# متون و فایل‌ها
# -----------------------------
def load_text_lines(path: str = "downloads/text.txt"):
    """خواندن همه‌ی خطوط غیرخالی از فایل text.txt"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f.read().splitlines() if ln.strip()]
    except FileNotFoundError:
        return []


# -----------------------------
# ساخت منشن و لینک‌ها
# -----------------------------
def make_mention_html(user_id: int, text: str) -> str:
    """ساخت منشن HTML تلگرام"""
    return f'<a href="tg://user?id={int(user_id)}">{html.escape(text)}</a>'


def chat_link_html(chat) -> str:
    """لینک HTML برای گروه/چت"""
    title = (chat.title or "").strip()
    if getattr(chat, "username", None):
        return f'<a href="https://t.me/{chat.username}">{html.escape(title)}</a>'
    return html.escape(title or str(chat.id))


# -----------------------------
# شبیه‌سازی تایپ کردن
# -----------------------------
async def maybe_typing(client, chat_id: int, seconds: int = 2):
    """نمایش 'typing...' برای مدت مشخص"""
    if not AllConfig.get("typing_on"):
        return
    end = time.time() + max(1, int(seconds))
    while time.time() < end:
        try:
            await client.send_chat_action(chat_id, "typing")
        except:
            pass
        await asyncio.sleep(3)


# -----------------------------
# متن کامل (برای enemy/kill)
# -----------------------------
def full_text(client, base_text: str) -> str:
    """ترکیب متن پایه با کپشن و منشن‌ها"""
    x = base_text
    if AllConfig.get("text_caption"):
        x += AllConfig["text_caption"]

    if AllConfig.get("is_menshen") and AllConfig.get("useridMen"):
        try:
            uid = int(AllConfig["useridMen"])
            text = AllConfig.get("textMen") or "mention"
            x += "\n" + make_mention_html(uid, text)
        except:
            pass

    if AllConfig.get("group_menshen") and AllConfig.get("group_ids"):
        mentions = [make_mention_html(uid, str(uid)) for uid in AllConfig["group_ids"]]
        if mentions:
            x += "\n" + " ".join(mentions)

    return x


# -----------------------------
# انتخاب یک متن خروجی
# -----------------------------
def out(client):
    """انتخاب یک خط تصادفی از text.txt و افزودن کپشن/منشن"""
    lines = load_text_lines()
    if not lines:
        return None
    base = random.choice(lines)
    return full_text(client, base)
