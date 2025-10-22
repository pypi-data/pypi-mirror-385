# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/relay/relay_commands.py

from __future__ import annotations
import re
import asyncio
from typing import Optional, Tuple, List

from pyrogram import filters
from pyrogram.types import Message
from SBself.config import AllConfig

# ---------- Admin Guard ----------
try:
    from SBself.filters.SBfilters import admin_filter as _project_admin_filter  # type: ignore
    ADMIN_FILTER = _project_admin_filter
except Exception:
    admin_ids = set(AllConfig.get("admin", {}).get("admins", []))
    ADMIN_FILTER = filters.user(list(admin_ids)) if admin_ids else filters.user([])

# ---------- Parsing ----------
RE_CMD_USER = re.compile(r"^(?:/?)(?:relay_user|for_this)(?:\s+.+)?$", re.IGNORECASE)
RE_CMD_FROM = re.compile(r"^(?:/?)(?:relay_from)(?:\s+.+)?$", re.IGNORECASE)
RE_USERNAME = re.compile(r"(?:https?://)?t\.me/([^/\s]+)", re.IGNORECASE)

def _split_args(text: str) -> List[str]:
    return text.strip().split()[1:] if text else []

def _take_flags(args: List[str]) -> Tuple[List[str], Optional[str]]:
    flags = {"--media", "--text"}
    found = [a for a in args if a in flags]
    args = [a for a in args if a not in flags]
    return args, (found[0] if found else None)

def _parse_user(text: str) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
    args = _split_args(text)
    args, flag = _take_flags(args)
    if len(args) == 2:                    # <SOURCE_ID> <DEST>
        return None, args[0], args[1], flag
    if len(args) == 3 and re.fullmatch(r"\d+", args[0]):
        return int(args[0]), args[1], args[2], flag
    return None, None, None, None

def _parse_from(text: str) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[int], Optional[str]]:
    args = _split_args(text)
    args, flag = _take_flags(args)
    if len(args) == 3 and re.fullmatch(r"\d+", args[0]):                 # <FROM_MSG_ID> <SOURCE_ID> <DEST>
        return int(args[0]), args[1], args[2], None, flag
    if len(args) == 4 and re.fullmatch(r"\d+", args[0]) and re.fullmatch(r"\d+", args[3]):  # + COUNT
        return int(args[0]), args[1], args[2], int(args[3]), flag
    return None, None, None, None, None

# ---------- Resolving ----------
async def _me_id(client) -> int:
    return int((await client.get_me()).id)

async def _resolve_id_token(client, token: str) -> Optional[int]:
    if token is None:
        return None
    t = token.strip()
    if t.lower() == "me":
        return await _me_id(client)
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except Exception:
            return None
    username = t[1:] if t.startswith("@") else None
    if not username:
        m = RE_USERNAME.search(t)
        if m:
            username = m.group(1).strip("/")
    if username:
        try:
            return int((await client.get_chat(username)).id)
        except Exception:
            try:
                return int((await client.get_users(username)).id)
            except Exception:
                return None
    return None

# ---------- Selection ----------
def _eligible(msg, source_id: int, flag: Optional[str]) -> bool:
    if getattr(msg, "outgoing", False):
        return False
    u = getattr(msg, "from_user", None)
    if not u or int(getattr(u, "id", 0)) != int(source_id):
        return False
    has_text = bool(getattr(msg, "text", None) or getattr(msg, "caption", None))
    has_media = bool(msg.media)
    if flag == "--media":
        return has_media
    if flag == "--text":
        return has_text and not has_media
    return has_text or has_media

async def _collect_incoming_ids(client, source_id: int, count: Optional[int],
                                min_msg_id: Optional[int], flag: Optional[str]) -> List[int]:
    ids: List[int] = []
    async for msg in client.get_chat_history(source_id):  # newest -> oldest
        mid = getattr(msg, "id", None) or getattr(msg, "message_id", None)
        if not mid:
            continue
        if min_msg_id is not None and int(mid) < int(min_msg_id):
            continue
        if _eligible(msg, source_id, flag):
            ids.append(int(mid))
        if count and len(ids) >= count:
            break
    ids.reverse()  # oldest -> newest
    return ids

# ---------- Forward ----------
async def _forward_in_batches(client, dest_id: int, source_id: int, message_ids: List[int],
                              batch: int = 100, delay: float = 0.25) -> int:
    sent = 0
    for i in range(0, len(message_ids), batch):
        chunk = message_ids[i:i + batch]
        try:
            await client.forward_messages(dest_id, source_id, chunk)
            sent += len(chunk)
        except Exception:
            for mid in chunk:
                try:
                    await client.forward_messages(dest_id, source_id, mid)
                    sent += 1
                    await asyncio.sleep(delay)
                except Exception:
                    pass
        await asyncio.sleep(delay)
    return sent

# ---------- Register ----------
def register_relay_commands(app):
    @app.on_message(ADMIN_FILTER & filters.regex(RE_CMD_USER))
    async def relay_user_cmd(client, m: Message):
        count, src_tok, dst_tok, flag = _parse_user(m.text or "")
        if not src_tok or not dst_tok:
            return await m.reply(
                "relay_user [COUNT] <SOURCE_ID> <DEST> [--media|--text]\n"
                "DEST: me | id | @username | t.me/..."
            )
        src = await _resolve_id_token(client, src_tok)
        dst = await _resolve_id_token(client, dst_tok)
        if src is None or dst is None:
            return await m.reply("SOURCE_ID یا DEST نامعتبر است.")
        ids = await _collect_incoming_ids(client, src, count, None, flag)
        if not ids:
            return await m.reply("پیامی مطابق فیلتر پیدا نشد.")
        n = await _forward_in_batches(client, dst, src, ids)
        await m.reply(f"✅ {n} پیام از `{src}` به `{dst}` فوروارد شد.")

    @app.on_message(ADMIN_FILTER & filters.regex(RE_CMD_FROM))
    async def relay_from_cmd(client, m: Message):
        from_id, src_tok, dst_tok, count, flag = _parse_from(m.text or "")
        if from_id is None or not src_tok or not dst_tok:
            return await m.reply(
                "relay_from <FROM_MSG_ID> <SOURCE_ID> <DEST> [COUNT] [--media|--text]\n"
                "DEST: me | id | @username | t.me/..."
            )
        src = await _resolve_id_token(client, src_tok)
        dst = await _resolve_id_token(client, dst_tok)
        if src is None or dst is None:
            return await m.reply("SOURCE_ID یا DEST نامعتبر است.")
        ids = await _collect_incoming_ids(client, src, count, from_id, flag)
        if not ids:
            return await m.reply("پیامی مطابق فیلتر/بازه پیدا نشد.")
        n = await _forward_in_batches(client, dst, src, ids)
        await m.reply(f"✅ {n} پیام از msg_id≥{from_id} کاربر `{src}` به `{dst}` فوروارد شد.")
