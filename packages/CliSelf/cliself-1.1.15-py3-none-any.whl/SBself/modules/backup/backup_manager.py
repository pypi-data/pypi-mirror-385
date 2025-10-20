# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/backup/backup_manager.py
"""
مدیریت بکاپ و گزارش حذف پیام‌ها (Private):

- ثبت پیام‌های خصوصی + ذخیرهٔ تمام مدیاها روی دیسک
- ساختار پوشهٔ جدا برای هر چت: <bk_dir>/<CHAT_ID>/
    - messages.txt
    - messages.json
    - messages.xlsx (در صورت وجود xlsxwriter)
    - media/
        - picture/
        - video/
        - voice/
        - music/
        - video_message/
        - document/
        - gif/
        - sticker/   (اختیاری ولی پشتیبانی می‌شود)
- تشخیص wipe و بکاپ خودکار (رویداد حذف + تشخیص از DB وقتی API خالی می‌شود)
- خروجی TXT با فرمت:
  YYYY-MM-DD HH:MM:SS | FROM_ID | FIRST LAST (ارسالی|دریافتی): TEXT [MEDIA_TAGS...]

نیازمندی‌های کانفیگ (AllConfig["backup"]):
    bk_enabled: bool
    bk_db: "downloads/backup.db"
    bk_dir: "downloads/bk_exports"
    bk_wipe_threshold: int
    bk_wipe_window_minutes: int (اگر نبود، 10)
    bk_cooldown_minutes: int (اگر نبود، 5)
"""

from __future__ import annotations
import os
import json
import time
import datetime
import sqlite3
from typing import Optional, List, Dict, Any, Tuple

from pyrogram.types import Message
from pyrogram.enums import ChatType
from ...config import AllConfig

# -----------------------------
# Logger
# -----------------------------
try:
    from ...core.logger import get_logger
    logger = get_logger("backup_manager")
except Exception:  # pragma: no cover
    import logging
    logger = logging.getLogger("backup_manager")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)


# =============================
#   🧱 Database Helpers
# =============================
def _db() -> sqlite3.Connection:
    cfg = AllConfig.get("backup", {})
    db_path = cfg.get("bk_db", "downloads/backup.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    # messages
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
    # deletions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deletions(
            chat_id     INTEGER,
            msg_id      INTEGER,
            deleted_at  INTEGER
        )
    """)
    # last backup cooldown
    conn.execute("""
        CREATE TABLE IF NOT EXISTS last_backups(
            chat_id     INTEGER PRIMARY KEY,
            last_backup INTEGER
        )
    """)
    # media
    conn.execute("""
        CREATE TABLE IF NOT EXISTS media(
            chat_id        INTEGER,
            msg_id         INTEGER,
            media_type     TEXT,
            file_id        TEXT,
            file_unique_id TEXT,
            file_name      TEXT,
            file_path      TEXT,
            mime_type      TEXT,
            size_bytes     INTEGER,
            width          INTEGER,
            height         INTEGER,
            duration       INTEGER,
            PRIMARY KEY(chat_id, msg_id, file_unique_id)
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


def db_count_msgs(chat_id: int) -> int:
    conn = _db()
    try:
        cur = conn.execute("SELECT COUNT(1) FROM msgs WHERE chat_id=?", (chat_id,))
        (n,) = cur.fetchone() or (0,)
        return int(n)
    finally:
        conn.close()


def db_fetch_msgs(chat_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
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


def db_fetch_media(chat_id: int, msg_id: int) -> List[Dict[str, Any]]:
    conn = _db()
    try:
        cur = conn.execute(
            "SELECT media_type,file_name,file_path,mime_type,size_bytes,width,height,duration "
            "FROM media WHERE chat_id=? AND msg_id=? ORDER BY media_type ASC",
            (chat_id, msg_id),
        )
        rows = []
        for mt, fn, fp, mime, size, w, h, dur in cur.fetchall():
            rows.append({
                "media_type": mt, "file_name": fn or "", "file_path": fp or "",
                "mime_type": mime or "", "size_bytes": int(size) if size else None,
                "width": int(w) if w else None, "height": int(h) if h else None,
                "duration": int(dur) if dur else None
            })
        return rows
    finally:
        conn.close()


# =============================
#   🧭 Paths & naming
# =============================
def _chat_dir(chat_id: int) -> str:
    bk_dir = AllConfig.get("backup", {}).get("bk_dir", "downloads/bk_exports")
    path = os.path.join(bk_dir, str(chat_id))
    os.makedirs(path, exist_ok=True)
    return path


def _media_root_for_chat(chat_id: int) -> str:
    root = os.path.join(_chat_dir(chat_id), "media")
    os.makedirs(root, exist_ok=True)
    return root


def _media_folder_name(telegram_media_attr: str) -> str:
    """
    نگاشت انواع تلگرام → نام پوشه
    photo→picture, video→video, animation→gif, voice→voice,
    audio→music, video_note→video_message, document→document, sticker→sticker
    """
    mapping = {
        "photo": "picture",
        "video": "video",
        "animation": "gif",
        "voice": "voice",
        "audio": "music",
        "video_note": "video_message",
        "document": "document",
        "sticker": "sticker",
    }
    return mapping.get(telegram_media_attr, telegram_media_attr)


def _media_path_for(chat_id: int, msg_id: int, kind: str, suggested_name: str = "", mime: str = "") -> str:
    kind_folder = _media_folder_name(kind)
    base = os.path.join(_media_root_for_chat(chat_id), kind_folder)
    os.makedirs(base, exist_ok=True)

    safe = "".join(c for c in (suggested_name or "") if c.isalnum() or c in ("-", "_", ".", " ")).strip()
    ext = ""
    if mime:
        mt = mime.lower()
        if "/" in mt:
            ext = "." + mt.split("/")[-1]
            if ext in (".jpeg",):
                ext = ".jpg"
    fname = f"{msg_id}_{kind_folder}"
    if safe:
        fname += "_" + safe
    if ext and not fname.endswith(ext):
        fname += ext
    return os.path.join(base, fname)


# =============================
#   🎛️ Public toggles & status
# =============================
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


# =============================
#   🧭 Small utilities
# =============================
def _name_display(first: str, last: str) -> str:
    full = (f"{first or ''} {last or ''}").strip()
    return full.upper() if full else ""


def _direction_label(outgoing: int) -> str:
    return "ارسالی" if int(outgoing) == 1 else "دریافتی"


# =============================
#   🖼️ Persist media for a message
# =============================
async def _persist_media_of_message(m: Message) -> None:
    """
    اگر پیام مدیا دارد، با ساختار پوشهٔ موردنظر ذخیره و متادیتا را ثبت می‌کند.
    """
    try:
        chat_id = m.chat.id
        msg_id = m.id

        def _insert(mt: str, file_id: str, file_unique_id: str, file_name: str,
                    file_path: str, mime: str, size: int,
                    width: int = None, height: int = None, duration: int = None):
            conn = _db()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO media(chat_id,msg_id,media_type,file_id,file_unique_id,"
                    "file_name,file_path,mime_type,size_bytes,width,height,duration) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (chat_id, msg_id, mt, file_id, file_unique_id, file_name, file_path, mime, size, width, height, duration)
                )
                conn.commit()
            finally:
                conn.close()

        async def _dl(kind: str, file_obj, suggested_name: str = ""):
            if not file_obj:
                return
            target = _media_path_for(chat_id, msg_id, kind, suggested_name, getattr(file_obj, "mime_type", ""))
            saved = await m.download(file_name=target)
            _insert(
                mt=_media_folder_name(kind),
                file_id=getattr(file_obj, "file_id", "") or "",
                file_unique_id=getattr(file_obj, "file_unique_id", "") or f"{kind}_{msg_id}",
                file_name=os.path.basename(saved or target),
                file_path=(saved or target),
                mime=(getattr(file_obj, "mime_type", "") or ""),
                size=int(getattr(file_obj, "file_size", 0) or 0),
                width=int(getattr(file_obj, "width", 0) or 0) or None,
                height=int(getattr(file_obj, "height", 0) or 0) or None,
                duration=int(getattr(file_obj, "duration", 0) or 0) or None,
            )

        if m.photo:
            await _dl("photo", m.photo)
        if m.video:
            await _dl("video", m.video, getattr(m.video, "file_name", "") or "")
        if m.animation:  # GIF
            await _dl("animation", m.animation, getattr(m.animation, "file_name", "") or "")
        if m.sticker:
            await _dl("sticker", m.sticker, "sticker")
        if m.voice:
            await _dl("voice", m.voice, "voice")
        if m.audio:
            await _dl("audio", m.audio, getattr(m.audio, "file_name", "") or "")
        if m.video_note:
            await _dl("video_note", m.video_note, "video_note")
        if m.document:
            await _dl("document", m.document, getattr(m.document, "file_name", "") or "")
    except Exception as e:
        logger.warning(f"_persist_media_of_message error: {e}")


# =============================
#   📝 Message Logging (with media)
# =============================
async def log_message(m: Message) -> None:
    """ذخیرهٔ پیام‌های private + مدیا برای بازسازی/گزارش و اکسپورت."""
    try:
        if not m or not m.chat or m.chat.type != ChatType.PRIVATE:
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
        conn.close()
        # media
        await _persist_media_of_message(m)
    except Exception as e:
        logger.warning(f"log_message error: {e}")


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


# =============================
#   📤 Export writers (under <bk_dir>/<CHAT_ID>/)
# =============================
def _write_exports(chat_id: int, me_id: int, rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    فایل‌ها را در مسیر: <bk_dir>/<CHAT_ID>/ ذخیره می‌کند.
    خروجی: مسیرهای ساخته‌شده {"txt": ..., "json": ..., "xlsx": (اختیاری)}
    """
    out_dir = _chat_dir(chat_id)
    paths: Dict[str, str] = {}

    # JSON
    try:
        json_path = os.path.join(out_dir, "messages.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        paths["json"] = json_path
    except Exception as e:
        logger.warning(f"write json failed: {e}")

    # TXT
    try:
        txt_path = os.path.join(out_dir, "messages.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for r in sorted(rows, key=lambda x: x["date"]):
                name_disp = _name_display(r.get("from_first",""), r.get("from_last",""))
                dir_lab = _direction_label(r["outgoing"])
                media_tags = ""
                if r.get("media"):
                    parts = []
                    for mi in r["media"]:
                        tag = f"{(mi['media_type'] or '').upper()}:{os.path.basename(mi.get('file_name') or mi.get('file_path',''))}"
                        parts.append(f"[{tag}]")
                    media_tags = (" " + " ".join(parts)) if parts else ""
                text_part = r.get("text","") or ""
                f.write(f"{_fmt_ts(r['date'])} | {r.get('from_id')} | {name_disp} ({dir_lab}): {text_part}{media_tags}\n")
        paths["txt"] = txt_path
    except Exception as e:
        logger.warning(f"write txt failed: {e}")

    # XLSX
    try:
        import xlsxwriter  # type: ignore
        xlsx_path = os.path.join(out_dir, "messages.xlsx")
        wb = xlsxwriter.Workbook(xlsx_path)
        ws = wb.add_worksheet("chat")
        headers = ["id", "date", "from_id", "from_first", "from_last",
                   "from_username", "outgoing", "text", "media_json"]
        ws.write_row(0, 0, headers)
        for i, r in enumerate(sorted(rows, key=lambda x: x["date"]), start=1):
            ws.write_row(i, 0, [
                r["id"], r["date"], r["from_id"], r.get("from_first",""), r.get("from_last",""),
                r.get("from_username",""), r["outgoing"], r.get("text",""),
                json.dumps(r.get("media") or [], ensure_ascii=False)
            ])
        wb.close()
        paths["xlsx"] = xlsx_path
    except Exception:
        pass

    return paths


# =============================
#   📤 Export via API (live)
# =============================
async def bk_export_dialog_for_user(client, user_id: int, limit: Optional[int] = None) -> Optional[str]:
    """
    اکسپورت تاریخچهٔ چت خصوصی از API. خروجی‌ها زیر <bk_dir>/<CHAT_ID>/ ذخیره می‌شوند.
    مسیر برگشتی: messages.txt (برای ارسال در تلگرام مناسب‌تر است)
    """
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
            "media": db_fetch_media(user_id, msg.id)  # اگر قبلاً ذخیره شده باشد، ضمیمه می‌شود
        })

    if not rows:
        return None

    me = await client.get_me()
    paths = _write_exports(chat_id=user_id, me_id=me.id, rows=rows)
    return paths.get("txt") or paths.get("json")


# =============================
#   📤 Export via DB (offline)
# =============================
async def bk_export_dialog_from_db(client, chat_id: int, limit: Optional[int] = None) -> Optional[str]:
    """
    اکسپورت از دیتابیس محلی؛ خروجی‌ها زیر <bk_dir>/<CHAT_ID>/ ذخیره می‌شوند.
    مسیر برگشتی: messages.txt
    """
    rows = db_fetch_msgs(chat_id, limit=limit)
    if not rows:
        return None

    # attach media per message
    for r in rows:
        r["media"] = db_fetch_media(chat_id, r["id"])

    me = await client.get_me()
    paths = _write_exports(chat_id=chat_id, me_id=me.id, rows=rows)
    return paths.get("txt") or paths.get("json")


# =============================
#   🧲 on_deleted: auto-backup on wipe
# =============================
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
    if not chat or chat.type != ChatType.PRIVATE or not ids:
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

    db_msgs = db_count_msgs(chat_id)
    wipe_detected = (recent >= threshold) or (db_msgs >= max(5, threshold) and api_empty)

    if wipe_detected and _cooldown_ok(chat_id, cooldown_min):
        # try API
        path = await bk_export_dialog_for_user(client, chat_id, limit=None)
        if not path:
            # fallback to DB
            path = await bk_export_dialog_from_db(client, chat_id, limit=None)

        if path:
            cap = f"🧳 Full backup after wipe\nChat: {chat_id}"
            try:
                await client.send_document("me", path, caption=cap)
            except Exception as e:
                logger.warning(f"send_document (wipe) failed: {e}")
            _save_last_backup(chat_id)
            logger.info(f"Full backup sent (wipe) for chat {chat_id}")
        return

    # اگر wipe نبود: گزارش خلاصه برای هر حذف
    del_ts = _now()
    for mid in ids:
        row = _fetch_msg(chat_id, mid)
        if not row:
            cap = (
                "🗑️ Deleted msg\n"
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


# =============================
#   🔎 Utilities for commands
# =============================
def list_media_files(chat_id: int, kind_folder: str) -> List[str]:
    """
    همهٔ فایل‌های یک نوع مدیا را از مسیر <bk_dir>/<CHAT_ID>/media/<kind_folder>/ برمی‌گرداند.
    kind_folder یکی از: picture/video/voice/music/video_message/document/gif/sticker
    """
    root = os.path.join(_media_root_for_chat(chat_id), kind_folder)
    if not os.path.isdir(root):
        return []
    files = []
    for nm in sorted(os.listdir(root)):
        p = os.path.join(root, nm)
        if os.path.isfile(p):
            files.append(p)
    return files
