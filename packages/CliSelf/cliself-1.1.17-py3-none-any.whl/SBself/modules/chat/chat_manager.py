# CliSelf/modules/chat_manager.py
import re
import asyncio
from pyrogram import Client, errors
from ...core.logger import get_logger

logger = get_logger("chat")

class ChatManager:
    """
    ChatManager
    ------------
    مدیریت ورود و خروج از گروه‌ها و کانال‌ها.
    پشتیبانی از انواع لینک‌ها:
    - invite link (https://t.me/+HASH یا https://t.me/joinchat/HASH)
    - public link (https://t.me/username)
    - direct username (@username)
    - chat_id عددی
    """

    def __init__(self, client: Client):
        self.client = client
        logger.info("ChatManager initialized successfully.")

    # ----------------------------------------------------------------
    # 🔹 تابع نرمال‌سازی ورودی (برگرفته از precise_engine در joiner)
    # ----------------------------------------------------------------
    def _normalize_target(self, raw: str):
        """
        ورودی را نرمالایز می‌کند و یکی از حالت‌ها را برمی‌گرداند:
          ('invite', invite_hash, original_has_joinchat)
          ('username', username, None)
          ('chat_id', int_chat_id, None)
        """
        if raw is None:
            return None, None, None

        s = str(raw).strip()
        original_has_joinchat = "joinchat" in s.lower()

        # حذف پروتکل و www
        s = re.sub(r'^(?:https?://)', '', s, flags=re.I)
        s = re.sub(r'^www\.', '', s, flags=re.I)

        # حذف مسیر اضافی
        if '/' in s:
            s = s.split('/')[-1]

        # اصلاح ورودی‌های اشتباه مانند Unity_Darkness.T.me
        m = re.search(r'^(?P<name>.*?)\.(?:t\.me|telegram\.me)$', s, flags=re.I)
        if m:
            s = m.group("name")

        s = s.split('?')[0].strip()
        s = s.strip('<> "\'')
        if s.startswith('@'):
            s = s[1:].strip()

        if s.startswith('+'):
            return 'invite', s.lstrip('+').strip(), False

        if s.lstrip('-').isdigit():
            try:
                return 'chat_id', int(s), None
            except Exception:
                pass

        if re.match(r'^[A-Za-z0-9_\-]{8,}$', s):
            if len(s) >= 20:
                return 'invite', s, original_has_joinchat
            return 'username', s, None

        return 'username', s, None

    # ----------------------------------------------------------------
    # 🔹 تابع جوین حرفه‌ای با پشتیبانی از همه‌ی حالات
    # ----------------------------------------------------------------
    async def join_chat(self, target: str):
        """
        جوین شدن به هر نوع لینک یا آیدی.
        پشتیبانی از لینک‌های دعوت، عمومی، @username، و chat_id.
        """
        try:
            if not target:
                raise ValueError("Target cannot be empty.")

            ttype, tval, aux = self._normalize_target(target)
            logger.info(f"Requested join target: {target} | Type: {ttype}")

            if ttype is None:
                raise ValueError("Invalid join target provided.")

            # انتخاب حالت مناسب برای پیوستن
            if ttype == 'invite':
                invite_hash = str(tval).lstrip('+').strip()
                invite_link = (
                    f"https://t.me/joinchat/{invite_hash}" if aux else f"https://t.me/+{invite_hash}"
                )
                try:
                    await self.client.join_chat(invite_link)
                    logger.info(f"✅ Joined via invite link: {invite_link}")
                    return f"✅ Joined via invite link."

                except errors.UserAlreadyParticipant:
                    logger.info(f"⚙️ Already in chat (invite link).")
                    return f"ℹ️ Already in chat."

                except errors.BadRequest as e:
                    logger.warning(f"⚠️ BadRequest on invite: {e}")
                    raise ValueError(f"Invite link invalid or expired: {invite_link}")

                except errors.FloodWait as e:
                    logger.warning(f"⏰ FloodWait {e.value}s on invite join.")
                    await asyncio.sleep(e.value)
                    raise TimeoutError(f"FloodWait: {e.value}s")

            elif ttype == 'chat_id':
                chat_id = tval
                try:
                    await self.client.join_chat(chat_id)
                    logger.info(f"✅ Joined chat_id: {chat_id}")
                    return f"✅ Joined chat: {chat_id}"

                except errors.UserAlreadyParticipant:
                    logger.info(f"⚙️ Already in chat_id {chat_id}")
                    return f"ℹ️ Already in chat."

                except errors.FloodWait as e:
                    logger.warning(f"⏰ FloodWait {e.value}s on chat_id join.")
                    await asyncio.sleep(e.value)
                    raise TimeoutError(f"FloodWait: {e.value}s")

            else:  # username
                username = str(tval).lstrip('@').strip()
                try:
                    await self.client.join_chat(username)
                    logger.info(f"✅ Joined public chat @{username}")
                    return f"✅ Joined public chat @{username}"

                except errors.UserAlreadyParticipant:
                    logger.info(f"⚙️ Already in public chat @{username}")
                    return f"ℹ️ Already in chat."

                except errors.UsernameInvalid:
                    logger.warning(f"⚠️ Invalid username @{username}")
                    raise ValueError(f"Invalid username @{username}")

                except errors.ChannelPrivate:
                    logger.warning(f"🔒 Cannot access @{username} (private or restricted)")
                    raise PermissionError(f"Cannot access @{username}, it may be private.")

                except errors.FloodWait as e:
                    logger.warning(f"⏰ FloodWait {e.value}s on username join.")
                    await asyncio.sleep(e.value)
                    raise TimeoutError(f"FloodWait: {e.value}s")

            raise ValueError(f"Unknown join type: {ttype}")

        except Exception as e:
            logger.error(f"❌ Join failed for target {target}: {type(e).__name__} - {e}")
            raise

    # ----------------------------------------------------------------
    # 🔹 تابع خروج از چت
    # ----------------------------------------------------------------
    async def leave_chat(self, identifier: str):
        """
        خروج از چت با استفاده از chat_id یا username.
        """
        try:
            if not identifier:
                raise ValueError("Chat identifier cannot be empty.")

            logger.info(f"Attempting to leave chat: {identifier}")
            try:
                chat_id = int(identifier)
            except ValueError:
                chat_id = identifier

            await self.client.leave_chat(chat_id)
            logger.info(f"✅ Left chat: {chat_id}")
            return f"✅ Left chat: {chat_id}"

        except Exception as e:
            logger.error(f"❌ Error leaving chat ({identifier}): {type(e).__name__} - {e}")
            raise
