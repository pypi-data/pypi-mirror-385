# -*- coding: utf-8 -*-
# File: SBself/spammer/auto_timer_handler.py
from ...config import AllConfig
from .spammer_via_schedule import schedule_next_message


# ------ Auto Timer Handler ------ #
async def handle_auto_timer(client, message):
    """
    هندلر خودکار تایمر — وقتی تایمر فعاله و پیام من با متن تایمر یکی باشه،
    پیام بعدی رو زمان‌بندی می‌کنه.
    """
    timer_cfg = AllConfig["timer"]
    if timer_cfg.get("auto"):
        if not timer_cfg.get("is_running"):
            return

        if message.text.strip() == timer_cfg.get("text", "").strip():
            next_interval = timer_cfg.get("last_interval", 0) + timer_cfg.get("time", 0)
            await schedule_next_message(client, next_interval)
