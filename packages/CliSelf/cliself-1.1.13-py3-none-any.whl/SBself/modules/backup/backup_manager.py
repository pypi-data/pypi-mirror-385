# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_manager.py
"""
مدیریت بکاپ و گزارش حذف پیام‌ها (Private):
- روشن/خاموش بکاپ
- ثبت پیام‌ها و حذف‌ها در SQLite
- تشخیص wipe و بکاپ خودکار به Saved Messages (هم با event حذف، هم با اتکا به DB)
- اکسپورت چت خصوصی به json/txt/xlsx با نام استاندارد

نیازمندی‌ها:
- AllConfig["backup"] شامل:
    bk_enabled: bool
    bk_db: مسیر DB (پیش‌فرض: downloads/backup.db)
    bk_dir: مسیر خروجی اکسپورت (پیش‌فرض: downloads/bk_exports)
    bk_wipe_threshold: int (آستانه حذف‌های سنگین)
    bk_wipe_window_minutes: int (اختیاری؛ پیش‌فرض 10)
    bk_cooldown_minutes: int (اختیاری؛ پیش‌فرض 5)
"""

from __future__ import annotations
import os
import json
import time
import datetime
import sqlite3
from typing import Optional, List, Dict, Any, Tuple

from pyrogram.types import Message
from ...config import AllConfig

# Logger پروژه
try:
    from ...core.logger import get_logger
    logger = get_logger("backup_manager")
except Exception:  # pragma: no cover
    import logging
    logger = logging.getLogger("backup_manager")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)


# -----------------------------
# 🧱 Database Helpers
# -----------------------------
def _db() -> sqlite3.Connection:
    cfg = AllConfig.get("backup", {})
    db_path = cfg.get("bk_db", "downloads/backup.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS msgs(
            chat_id     INTEGER,
            msg_id      INTEGER,
            ts_sent     INTEGER,
            outgoing    INTEGER,
            from_id     INTEGER,
            first_name  TEXT,
            last_name   TEXT,
            username    TEXT,
            text        TEXT,
            PRIMARY KEY(chat_id, msg_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deletions(
            chat_id     INTEGER,
            msg_id      INTEGER,
            deleted_at  INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS last_backups(
            chat_id     INTEGER PRIMARY KEY,
            last_backup INTEGER
        )
    """)
    return conn


def _now() -> int:
    return int(time.time())


def _fmt_ts(ts: int) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _save_last_backup(chat_id: int) -> None:
    conn = _db()
    try:
        conn.execute(
            "INSERT INTO last_backups(chat_id,last_backup) VALUES(?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET last_backup=excluded.last_backup",
            (chat_id, _now()),
        )
        conn.commit()
    finally:
        conn.close()


def _cooldown_ok(chat_id: int, minutes: int) -> bool:
    conn = _db()
    try:
        cur = conn.execute("SELECT last_backup FROM last_backups WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        if not row:
            return True
        return (_now() - int(row[0])) >= minutes * 60
    finally:
        conn.close()


def _count_recent_deletions(chat_id: int, window_minutes: int) -> int:
    since = _now() - window_minutes * 60
    conn = _db()
    try:
        cur = conn.execute(
            "SELECT COUNT(1) FROM deletions WHERE chat_id=? AND deleted_at>=?",
            (chat_id, since),
        )
        (n,) = cur.fetchone() or (0,)
        return int(n)
    finally:
        conn.close()


def _fetch_msg(chat_id: int, msg_id: int) -> Optional[Tuple[int, int, int, str, str, str, str]]:
    conn = _db()
    try:
        cur = conn.execute(
            "SELECT ts_sent,outgoing,from_id,first_name,last_name,username,text "
            "FROM msgs WHERE chat_id=? AND msg_id=?",
            (chat_id, msg_id),
        )
        return cur.fetchone()
    finally:
        conn.close()


# >>> NEW: Helpers to read from DB for full export even if API history is gone
def db_count_msgs(chat_id: int) -> int:
    conn = _db()
    try:
        cur = conn.execute("SELECT COUNT(1) FROM msgs WHERE chat_id=?", (chat_id,))
        (n,) = cur.fetchone() or (0,)
        return int(n)
    finally:
        conn.close()


def db_fetch_msgs(chat_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    پیام‌ها را از DB می‌خواند؛ اگر limit None باشد، همه را زمان‌صعودی می‌دهد،
    وگرنه فقط آخرین limit پیام.
    """
    conn = _db()
    try:
        base_q = (
            "SELECT msg_id,ts_sent,from_id,first_name,last_name,username,outgoing,text "
            "FROM msgs WHERE chat_id=? ORDER BY ts_sent ASC"
        )
        if limit is None:
            cur = conn.execute(base_q, (chat_id,))
        else:
            cur = conn.execute(base_q + " LIMIT ?", (chat_id, int(limit)))
        rows = []
        for (mid, ts, from_id, fn, ln, un, outgoing, text) in cur.fetchall():
            rows.append({
                "id": mid, "date": int(ts),
                "from_id": from_id, "from_first": fn, "from_last": ln, "from_username": un,
                "outgoing": int(outgoing), "text": text or ""
            })
        return rows
    finally:
        conn.close()


# -----------------------------
# 🎛️ Public toggles & status
# -----------------------------
async def bk_on() -> str:
    AllConfig["backup"]["bk_enabled"] = True
    logger.info("✅ Backup ON")
    return "✅ بکاپ فعال شد."


async def bk_off() -> str:
    AllConfig["backup"]["bk_enabled"] = False
    logger.info("🛑 Backup OFF")
    return "🛑 بکاپ غیرفعال شد."


async def bk_status() -> str:
    cfg = AllConfig["backup"]
    return (
        "📊 وضعیت بکاپ:\n"
        f"- enabled: {cfg.get('bk_enabled')}\n"
        f"- db: {cfg.get('bk_db')}\n"
        f"- dir: {cfg.get('bk_dir')}\n"
        f"- wipe_threshold: {cfg.get('bk_wipe_threshold')}\n"
        f"- wipe_window_minutes: {cfg.get('bk_wipe_window_minutes', 10)}\n"
        f"- cooldown_minutes: {cfg.get('bk_cooldown_minutes', 5)}\n"
    )


# -----------------------------
# 📝 Message/Deletion Logging
# -----------------------------
async def log_message(m: Message) -> None:
    """ذخیره پیام‌های private برای بازسازی و گزارش حذف."""
    try:
        if not m or not m.chat or m.chat.type != "private":
            return
        u = getattr(m, "from_user", None)
        from_id = u.id if u else 0
        fn = (u.first_name or "") if u else ""
        ln = (u.last_name or "") if u else ""
        un = (u.username or "") if u else ""
        conn = _db()
        conn.execute(
            "INSERT OR REPLACE INTO msgs(chat_id,msg_id,ts_sent,outgoing,from_id,first_name,last_name,username,text) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                m.chat.id,
                m.id,
                int(m.date.timestamp()) if m.date else _now(),
                1 if m.outgoing else 0,
                from_id, fn, ln, un,
                (m.text or m.caption or ""),
            ),
        )
        conn.commit()
    except Exception as e:
        logger.warning(f"log_message error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


async def _log_deletions(chat_id: int, ids: List[int]) -> None:
    if not ids:
        return
    conn = _db()
    try:
        now = _now()
        conn.executemany(
            "INSERT INTO deletions(chat_id,msg_id,deleted_at) VALUES(?,?,?)",
            [(chat_id, mid, now) for mid in ids],
        )
        conn.commit()
    finally:
        conn.close()


# -----------------------------
# 📤 Export via API (live history)
# -----------------------------
async def bk_export_dialog_for_user(client, user_id: int, limit: Optional[int] = None) -> Optional[str]:
    """
    اکسپورت تاریخچهٔ چت خصوصی با user_id از API.
    limit=None یعنی همهٔ پیام‌ها.
    خروجی ترجیحاً xlsx؛ اگر xlsxwriter موجود نباشد txt برمی‌گردد.
    """
    cfg = AllConfig["backup"]
    out_dir = cfg.get("bk_dir", "downloads/bk_exports")
    os.makedirs(out_dir, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    async for msg in client.get_chat_history(user_id, limit=limit):
        u = getattr(msg, "from_user", None)
        rows.append({
            "id": msg.id,
            "date": int(msg.date.timestamp()) if msg.date else _now(),
            "from_id": (u.id if u else None),
            "from_first": (u.first_name or "") if u else "",
            "from_last": (u.last_name or "") if u else "",
            "from_username": (u.username or "") if u else "",
            "outgoing": 1 if msg.outgoing else 0,
            "text": (msg.text or msg.caption or ""),
        })

    if not rows:
        return None

    me = await client.get_me()
    stem = f"backup [ {me.id} - {user_id} ]"
    base = os.path.join(out_dir, stem)

    # JSON
    try:
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"write json failed: {e}")

    # TXT
    try:
        with open(base + ".txt", "w", encoding="utf-8") as f:
            for r in sorted(rows, key=lambda x: x["date"]):
                f.write(
                    f"{_fmt_ts(r['date'])} | {r['from_id']} "
                    f"({'out' if r['outgoing'] else 'in'}): {r['text']}\n"
                )
    except Exception as e:
        logger.warning(f"write txt failed: {e}")

    # XLSX (optional)
    path_ret: Optional[str] = None
    try:
        import xlsxwriter  # type: ignore
        wb = xlsxwriter.Workbook(base + ".xlsx")
        ws = wb.add_worksheet("chat")
        headers = ["id", "date", "from_id", "from_first", "from_last",
                   "from_username", "outgoing", "text"]
        ws.write_row(0, 0, headers)
        for i, r in enumerate(sorted(rows, key=lambda x: x["date"]), start=1):
            ws.write_row(i, 0, [
                r["id"], r["date"], r["from_id"], r["from_first"], r["from_last"],
                r["from_username"], r["outgoing"], r["text"]
            ])
        wb.close()
        path_ret = base + ".xlsx"
    except Exception:
        path_ret = base + ".txt"

    logger.info(f"📤 Exported dialog via API: {path_ret}")
    return path_ret


# -----------------------------
# 📤 Export via DB (offline/local)
# -----------------------------
async def bk_export_dialog_from_db(client, chat_id: int, limit: Optional[int] = None) -> Optional[str]:
    """
    اکسپورت از دیتابیس محلی msgs؛ حتی اگر پیام‌ها از سرور پاک شده باشند.
    """
    cfg = AllConfig["backup"]
    out_dir = cfg.get("bk_dir", "downloads/bk_exports")
    os.makedirs(out_dir, exist_ok=True)

    rows = db_fetch_msgs(chat_id, limit=limit)
    if not rows:
        return None

    me = await client.get_me()
    stem = f"backup [ {me.id} - {chat_id} ]"
    base = os.path.join(out_dir, stem)

    # JSON
    try:
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"write json (db) failed: {e}")

    # TXT
    try:
        with open(base + ".txt", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(f"{_fmt_ts(r['date'])} | {r['from_id']} "
                        f"({'out' if r['outgoing'] else 'in'}): {r['text']}\n")
    except Exception as e:
        logger.warning(f"write txt (db) failed: {e}")

    # XLSX
    path_ret: Optional[str] = None
    try:
        import xlsxwriter  # type: ignore
        wb = xlsxwriter.Workbook(base + ".xlsx")
        ws = wb.add_worksheet("chat")
        headers = ["id", "date", "from_id", "from_first", "from_last", "from_username", "outgoing", "text"]
        ws.write_row(0, 0, headers)
        for i, r in enumerate(rows, start=1):
            ws.write_row(i, 0, [
                r["id"], r["date"], r["from_id"], r.get("from_first",""), r.get("from_last",""),
                r.get("from_username",""), r["outgoing"], r["text"]
            ])
        wb.close()
        path_ret = base + ".xlsx"
    except Exception:
        path_ret = base + ".txt"

    logger.info(f"📤 Exported dialog from DB: {path_ret}")
    return path_ret


# -----------------------------
# 🧲 on_deleted: auto-backup on wipe (event + DB-aware)
# -----------------------------
async def on_deleted(client, deleted_event) -> None:
    """
    روی حذف پیام در چت خصوصی:
      - حذف‌ها را ثبت می‌کند
      - اگر تعداد حذف‌های پنجرهٔ زمانی اخیر >= آستانه → بکاپ کامل و ارسال به Saved Messages
      - اگر API خالی و DB پر باشد → بکاپ کامل از DB
      - در غیر اینصورت برای هر پیام حذف‌شده، خلاصه‌ای به Saved Messages می‌فرستد
    """
    cfg = AllConfig["backup"]
    if not cfg.get("bk_enabled", False):
        return

    chat = getattr(deleted_event, "chat", None)
    ids = getattr(deleted_event, "messages_ids", None) or getattr(deleted_event, "messages", None) or []
    if not chat or chat.type != "private" or not ids:
        return

    chat_id = chat.id
    await _log_deletions(chat_id, list(ids))

    threshold = int(cfg.get("bk_wipe_threshold", 50))
    window_min = int(cfg.get("bk_wipe_window_minutes", 10))
    cooldown_min = int(cfg.get("bk_cooldown_minutes", 5))

    recent = _count_recent_deletions(chat_id, window_min)

    # آیا تاریخچه API الان خالی است؟
    api_empty = True
    try:
        async for _ in client.get_chat_history(chat_id, limit=1):
            api_empty = False
            break
    except Exception:
        api_empty = True

    # وضعیت DB
    db_msgs = db_count_msgs(chat_id)

    # تشخیص wipe: یا شمارش حذف‌ها، یا ناگهانی خالی‌شدن API درحالی‌که DB پر است
    wipe_detected = (recent >= threshold) or (db_msgs >= max(5, threshold) and api_empty)

    if wipe_detected and _cooldown_ok(chat_id, cooldown_min):
        # تلاش اول: اگر API چیزی داشته باشد
        path = await bk_export_dialog_for_user(client, chat_id, limit=None)
        # اگر چیزی نبود، از DB فول‌بکاپ بگیر
        if not path:
            path = await bk_export_dialog_from_db(client, chat_id, limit=None)

        if path:
            name_part = f"{(getattr(chat,'first_name','') or '').strip()} {(getattr(chat,'last_name','') or '').strip()}".strip()
            cap = f"🧳 Full backup after wipe\nChat: {name_part} ({chat_id})"
            try:
                await client.send_document("me", path, caption=cap)
            except Exception as e:
                logger.warning(f"send_document (wipe) failed: {e}")
            _save_last_backup(chat_id)
            logger.info(f"Full backup sent (wipe) for chat {chat_id}")
        return

    # اگر wipe نبود: ریزگزارش حذف
    del_ts = _now()
    for mid in ids:
        row = _fetch_msg(chat_id, mid)
        if not row:
            cap = (
                "🗑️ Deleted msg\n"
                f"👤 {(getattr(chat,'first_name','') or '').strip()} {(getattr(chat,'last_name','') or '').strip()} @{(getattr(chat,'username','') or '')}\n"
                f"💬 Chat ID: {chat_id}\n"
                f"🕓 Deleted at: {_fmt_ts(del_ts)}"
            )
            try:
                await client.send_message("me", cap.strip())
            except Exception as e:
                logger.warning(f"send_message (deleted brief) failed: {e}")
            continue

        ts_sent, outgoing, from_id, fn, ln, un, txt = row
        cap = (
            "🗑️ Deleted message\n"
            f"👤 From: {(fn + ' ' + ln).strip()}{(' @' + un) if un else ''} ({from_id})\n"
            f"💬 Chat ID: {chat_id}\n"
            f"🕓 Sent at: {_fmt_ts(ts_sent)}\n"
            f"🕓 Deleted at: {_fmt_ts(del_ts)}\n"
            f"---\n{txt}"
        )
        try:
            await client.send_message("me", cap)
        except Exception as e:
            logger.warning(f"send_message (deleted detail) failed: {e}")
        logger.info(f"Deleted message logged from chat {chat_id}, msg {mid}")
