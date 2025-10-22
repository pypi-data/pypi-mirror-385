# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/id_manager.py

from .utils import make_mention_html, chat_link_html


async def get_id_info(client, message) -> str:
    """
    نمایش اطلاعات کاربر یا چت.
    - اگر ریپلای باشه: اطلاعات فرد ریپلای‌شده
    - اگر آرگومان باشه: اطلاعات اون یوزر/چت
    - در غیر اینصورت: اطلاعات خود پیام‌دهنده
    """
    target = None
    reply = message.reply_to_message

    if reply and reply.from_user:
        target = reply.from_user
    elif len(message.command) > 1:
        query = message.command[1]
        try:
            target = await client.get_users(query)
        except:
            try:
                target = await client.get_chat(query)
            except:
                return "❌ کاربر/چت پیدا نشد."
    else:
        target = message.from_user

    if not target:
        return "❌ کاربر/چت پیدا نشد."

    if hasattr(target, "id"):  # کاربر
        name = (target.first_name or "") + (" " + target.last_name if target.last_name else "")
        uname = f"@{target.username}" if target.username else "-"
        mention = make_mention_html(target.id, name or str(target.id))
        return (
            f"👤 ID اطلاعات:\n"
            f"- ID: {target.id}\n"
            f"- Name: {name.strip() or '-'}\n"
            f"- Username: {uname}\n"
            f"- Mention: {mention}"
        )

    if hasattr(target, "title"):  # چت/گروه
        title = target.title
        uname = f"@{target.username}" if target.username else "-"
        link = chat_link_html(target)
        return (
            f"👥 Chat اطلاعات:\n"
            f"- ID: {target.id}\n"
            f"- Title: {title}\n"
            f"- Username: {uname}\n"
            f"- Link: {link}"
        )

    return "❌ نوع ناشناخته."
