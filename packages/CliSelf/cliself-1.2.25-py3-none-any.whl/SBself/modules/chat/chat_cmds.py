# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/chat_cmds.py

from .chat_manager import ChatManager
from .chat_cleaner import ChatCleaner

chat_manager = None
cleaner = None


def init_chat_tools(app):
    """Initialize managers with app instance."""
    global chat_manager, cleaner
    chat_manager = ChatManager(app)
    cleaner = ChatCleaner(app)


# -----------------------------
# Chat join/leave
# -----------------------------
async def join_chat(target: str) -> str:
    return await chat_manager.join_chat(target)


async def leave_chat(target: str) -> str:
    return await chat_manager.leave_chat(target)


# -----------------------------
# Chat cleaning
# -----------------------------
async def clear_all(chat_id: int, title: str) -> str:
    return await cleaner.clear_all(chat_id, title)


async def clear_last(chat_id: int, n: int, current_msg_id: int) -> str:
    return await cleaner.clear_last(chat_id, n, current_msg_id=current_msg_id)
