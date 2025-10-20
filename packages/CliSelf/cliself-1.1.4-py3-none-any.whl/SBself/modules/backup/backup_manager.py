# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup_manager.py

import os
import json
import time
import asyncio
import datetime
import sqlite3
from typing import Optional, Tuple, Any
from pyrogram.types import Message
from ...config import AllConfig

# تلاش برای استفاده از logger پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("backup_manager")
except Exception:
    import logging
    logger = logging.getLogger("backup_manager")


# -----------------------------
# 🧱 Database Helpers
# -----------------------------
def _db():
    """اتصال به دیتابیس بکاپ، در صورت عدم وجود، جدول را می‌سازد."""
    db_path = AllConfig["backup"].get("bk_db", "downloads/backup.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS msgs (
            chat_id INTEGER,
            msg_id INTEGER,
            ts_sent INTEGER,
            outgoing INTEGER,
            from_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            text TEXT,
            PRIMARY KEY(chat_id, msg_id)
        )
    """)
    return conn


def _now() -> int:
    return int(time.time())


def _fmt_ts(ts: int) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _uinfo(m: Message) -> Tuple[Optional[int], str, str, str]:
    """برگشت اطلاعات کاربر از پیام"""
    u = getattr(m, "from_user", None)
    if u:
        return (u.id, (u.first_name or ""), (u.last_name or ""), (u.username or ""))
    return (None, "", "", "")


def _fetch_msg(chat_id: int, msg_id: int):
    """برگشت یک پیام ذخیره‌شده از دیتابیس"""
    conn = _db()
    try:
        cur = conn.execute(
            "SELECT ts_sent,outgoing,from_id,first_name,last_name,username,text "
            "FROM msgs WHERE chat_id=? AND msg_id=?",
            (chat_id, msg_id)
        )
        return cur.fetchone()
    finally:
        conn.close()


def _distinct_dm_count() -> int:
    """تعداد چت‌های منحصربه‌فرد در دیتابیس"""
    conn = _db()
    try:
        cur = conn.execute("SELECT COUNT(DISTINCT chat_id) FROM msgs")
        c = cur.fetchone()
        return int(c[0]) if c else 0
    finally:
        conn.close()


# -----------------------------
# ⚙️ Public API (main interface)
# -----------------------------
async def bk_on() -> str:
    AllConfig["backup"]["bk_enabled"] = True
    logger.info("✅ Backup turned ON")
    return "✅ بکاپ فعال شد."


async def bk_off() -> str:
    AllConfig["backup"]["bk_enabled"] = False
    logger.info("🛑 Backup turned OFF")
    return "🛑 بکاپ غیرفعال شد."


async def bk_status() -> str:
    cfg = AllConfig["backup"]
    return (
        f"📊 **وضعیت بکاپ:**\n"
        f"🟢 فعال: {'✅' if cfg['bk_enabled'] else '❌'}\n"
        f"💾 دیتابیس: `{cfg['bk_db']}`\n"
        f"📁 مسیر خروجی: `{cfg['bk_dir']}`\n"
        f"🚫 آستانه حذف: {cfg['bk_wipe_threshold']}\n"
        f"💬 چت‌ها در DB: {_distinct_dm_count()}"
    )


async def bk_set_threshold(n: int) -> str:
    if n < 1:
        return "❌ عدد معتبر بده."
    AllConfig["backup"]["bk_wipe_threshold"] = n
    logger.info(f"🧮 Threshold set to {n}")
    return f"✅ آستانه حذف روی {n} تنظیم شد."


# -----------------------------
# 💬 Log Messages
# -----------------------------
async def bk_log_private(m: Message) -> None:
    """ثبت پیام خصوصی در دیتابیس بکاپ"""
    cfg = AllConfig["backup"]
    if not cfg["bk_enabled"] or not m or m.chat.type != "private":
        return

    conn = _db()
    uid, fn, ln, un = _uinfo(m)
    txt = m.text or m.caption or ""
    try:
        conn.execute(
            "INSERT OR REPLACE INTO msgs VALUES(?,?,?,?,?,?,?,?,?)",
            (
                m.chat.id,
                m.id,
                int(m.date.timestamp()) if m.date else _now(),
                1 if m.outgoing else 0,
                uid or 0,
                fn,
                ln,
                un,
                txt,
            ),
        )
        conn.commit()
        logger.debug(f"📝 Logged message {m.id} from chat {m.chat.id}")
    except Exception as e:
        logger.error(f"⚠️ Error logging message: {e}")
    finally:
        conn.close()


# -----------------------------
# 📤 Export Helpers
# -----------------------------
def _export_dialog(chat_id: int) -> Optional[str]:
    """ذخیره یک دیالوگ کامل در قالب JSONL"""
    cfg = AllConfig["backup"]
    conn = _db()
    try:
        cur = conn.execute(
            "SELECT msg_id,ts_sent,outgoing,from_id,first_name,last_name,username,text "
            "FROM msgs WHERE chat_id=? ORDER BY msg_id",
            (chat_id,),
        )
        rows = cur.fetchall()
        if not rows:
            return None

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bk_dir = cfg.get("bk_dir", "downloads/bk_exports")
        os.makedirs(bk_dir, exist_ok=True)
        path = os.path.join(bk_dir, f"dialog_{chat_id}_{ts}.jsonl")

        with open(path, "w", encoding="utf-8") as f:
            for (mid, ts_sent, out, from_id, fn, ln, un, txt) in rows:
                record = {
                    "chat_id": chat_id,
                    "msg_id": mid,
                    "ts_sent": ts_sent,
                    "outgoing": out,
                    "from_id": from_id,
                    "first_name": fn,
                    "last_name": ln,
                    "username": un,
                    "text": txt,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"📤 Exported dialog for chat {chat_id} → {path}")
        return path
    finally:
        conn.close()


async def bk_export_dialog_for_user(uid: int) -> Optional[str]:
    """خروجی گرفتن از دیالوگ با شناسه کاربر"""
    return _export_dialog(uid)


# -----------------------------
# 🗑️ Deleted Messages Handler
# -----------------------------
async def on_deleted(client, deleted_event) -> None:
    """
    هندلر حذف پیام‌ها (استفاده در main.py)
    - اگر پیام زیاد حذف شد، کل چت export می‌شود
    - در غیر اینصورت، هر پیام حذف‌شده جداگانه به Saved Messages فرستاده می‌شود
    """
    cfg = AllConfig["backup"]
    if not cfg["bk_enabled"]:
        return

    chat = getattr(deleted_event, "chat", None)
    ids = getattr(deleted_event, "messages_ids", None) or getattr(deleted_event, "messages", None) or []
    if not chat or chat.type != "private" or not ids:
        return

    chat_id = chat.id
    del_ts = _now()
    threshold = int(cfg["bk_wipe_threshold"])

    # اگر پاک‌سازی گسترده باشد → export کل چت
    if len(ids) >= threshold:
        path = _export_dialog(chat_id)
        if path:
            cap = f"⚠️ Chat wiped: {(chat.first_name or '').strip()} {(chat.last_name or '').strip()} ({chat_id})"
            await client.send_document("me", path, caption=cap)
            logger.warning(f"🚨 Chat {chat_id} wiped and exported.")
        return

    # در غیر اینصورت → ارسال پیام‌های حذف‌شده تکی
    for mid in ids:
        row = _fetch_msg(chat_id, mid)
        if not row:
            cap = (
                f"🗑️ Deleted msg\n"
                f"👤 {(chat.first_name or '').strip()} {(chat.last_name or '').strip()} @{(chat.username or '')}\n"
                f"💬 Chat ID: {chat_id}\n"
                f"🕓 Deleted at: {_fmt_ts(del_ts)}"
            )
            await client.send_message("me", cap.strip())
            continue

        ts_sent, outgoing, from_id, fn, ln, un, txt = row
        cap = (
            f"🗑️ Deleted message\n"
            f"👤 From: {(fn + ' ' + ln).strip()}{(' @' + un) if un else ''} ({from_id})\n"
            f"💬 Chat ID: {chat_id}\n"
            f"🕓 Sent at: {_fmt_ts(ts_sent)}\n"
            f"🕓 Deleted at: {_fmt_ts(del_ts)}\n"
            f"---\n{txt}"
        )
        await client.send_message("me", cap)
        logger.info(f"🗑️ Deleted message logged from chat {chat_id}, msg {mid}")
