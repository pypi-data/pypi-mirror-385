# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/forward_cmds.py

from .forward_manager import ForwardManager
from .forward_queue_manager import ForwardQueueManager

forwarder = None
fwd_mgr = None


def init_forward_tools(app):
    """Initialize forward managers with app instance."""
    global forwarder, fwd_mgr
    forwarder = ForwardManager(app)
    fwd_mgr = ForwardQueueManager(app)


async def forward_all(src: str, dest: str) -> str:
    """
    انتقال تمام پیام‌ها از src به dest
    مثال:
        forward_all("@somechat", "me")
    """
    return await forwarder.forward_all(src, dest)
