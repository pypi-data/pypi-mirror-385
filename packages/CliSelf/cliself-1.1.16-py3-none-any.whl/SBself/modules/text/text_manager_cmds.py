# -*- coding: utf-8 -*-
# File: CliSelf/SBself/modules/text_manager_cmds.py

from ...config import AllConfig
from .text_manager import TextManager

text_mgr = TextManager()


# -------------------------------
# افزودن یک خط متن
# -------------------------------
async def add_text(txt: str) -> str:
    if not txt.strip():
        return "❌ متنی وارد نشد."
    return await text_mgr.add_text(txt)


# -------------------------------
# افزودن چند خط متن
# -------------------------------
async def add_all_text(txt: str) -> str:
    if not txt.strip():
        return "❌ متنی برای ذخیره وجود ندارد."
    return await text_mgr.add_all_text(txt)


# -------------------------------
# حذف یک خط خاص
# -------------------------------
async def del_text(txt: str) -> str:
    if not txt.strip():
        return "❌ متنی برای حذف وارد نشده."
    return await text_mgr.delete_text(txt)


# -------------------------------
# پاکسازی کل فایل
# -------------------------------
async def clear_text() -> str:
    return await text_mgr.clear_text()


# -------------------------------
# تنظیم کپشن
# -------------------------------
async def set_caption(txt: str) -> str:
    if not txt.strip():
        return "❌ کپشن خالی است."
    result = await text_mgr.set_caption(txt)
    AllConfig["spammer"]["text_caption"] = txt.strip()
    return result


# -------------------------------
# پاکسازی کپشن
# -------------------------------
async def clear_caption() -> str:
    result = await text_mgr.clear_caption()
    AllConfig["spammer"]["text_caption"] = ""
    return result


# -------------------------------
# دریافت کپشن فعلی
# -------------------------------
async def get_caption() -> str:
    return await text_mgr.get_caption()
