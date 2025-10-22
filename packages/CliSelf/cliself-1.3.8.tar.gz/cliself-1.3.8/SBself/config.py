# -*- coding: utf-8 -*-
# File: SBself/config.py
#
# ⚙️ پیکربندی مرکزی برنامه
# - از این نسخه، «تکست‌ها» در AllConfig["text"]["lines"] نگهداری می‌شوند
# - نیازی به فایل downloads/text.txt نیست
# - هِلپر اختیاری migrate_legacy_texts برای انتقال یک‌باره از فایل قدیمی فراهم شده

import os
from typing import List, Dict, Any

# ---------------------------
# 👥 لیست ادمین‌ها
# ---------------------------
adminList = [5053851121]

# ---------------------------
# 🧠 تنظیمات کلی اپلیکیشن
# ---------------------------
app_config: Dict[str, Any] = {
    "name": "app",
    "api_id": 17221354,
    "api_hash": "b86bbf4b700b4e922fff2c05b3b8985f",
    "number": "+989013728416",
    "password": "mmd0@0mmd",
}

# ---------------------------
# 💬 اسپمر و پیام‌رسانی خودکار
# ---------------------------
spammer_config: Dict[str, Any] = { 
    "time": 10,
    "run_spammer": False,
    "run_kill": False,
    "typing_on": False,
    "targets": [],  
    
}

# ---------------------------
# 🧍‍♂️ تنظیمات منشن‌ها
# ---------------------------
mention_config: Dict[str, Any] = {
    "textMen": "",
    "useridMen": "",
    "is_menshen": False,
    "group_menshen": False,
    "group_ids": [],
}

# ---------------------------
# 😡 دشمن‌ها و mute
# ---------------------------
enemy_config: Dict[str, Any] = {
    "enemy": [],
    "special_enemy": [],
    "enemy_ignore": 0,
    "enemy_counter": {},
    "mute": [],
    "specialenemytext": [],
    "SPTimelist": [],
}

# ---------------------------
# 👮‍♂️ ادمین‌ها
# ---------------------------
admin_config: Dict[str, Any] = {
    "admins": [5053851121],
}

# ---------------------------
# 📝 تغییر نام خودکار
# ---------------------------
names_config: Dict[str, Any] = {
    "names": [],
    "change_interval_h": 1,
    "changenames": False,
    "changenames_idx": 0,
    "changenames_task": None,
}

# ---------------------------
# 💾 بکاپ و پایگاه داده
# ---------------------------
backup_config: Dict[str, Any] = {
    "bk_enabled": True,
    "bk_db": "downloads/backup.db",
    "bk_dir": "downloads/bk_exports",
    "bk_wipe_threshold": 10,
    "bk_wipe_window_minutes": 1,   # پنجرهٔ شمارش حذف‌ها برای تشخیص wipe
    "bk_cooldown_minutes": 1,      # کول‌داون برای جلوگیری از اسپم بکاپ
}

# ---------------------------
# 📷 تنظیمات مدیا
# ---------------------------
media_config: Dict[str, Any] = {
    "catch_view_once": True,
}

# ---------------------------
# ⏱ تایمر پیام‌ها
# ---------------------------
timer_config: Dict[str, Any] = {
    "text": "",
    "time": 0,
    "chat_id": None,
    "first_time": None,
    "last_interval": 0,
    "repeat": 100,
    "message_ids": [],
    "is_running": False,
    "auto": False,
    "targets": [],  
}

# ---------------------------
# 🧾 متن‌ها (جایگزین فایل text.txt)
# --------------------------- 
text_config: Dict[str, Any] = {
    "lines": [],   # لیست رشته‌ها
    "caption":"",
}

# ---------------------------
# ⚙️ ترکیب همه‌ی تنظیمات در AllConfig
# ---------------------------
AllConfig: Dict[str, Any] = {
    "app": app_config,
    "spammer": spammer_config,
    "mention": mention_config,
    "enemy": enemy_config,
    "admin": admin_config,
    "names": names_config,
    "backup": backup_config,
    "media": media_config,
    "timer": timer_config,
    "text": text_config,       # ← مهم: بخش جدید متن‌ها
    "owners": []
}


# ---------------------------
# 🔁 تابع ریست تنظیمات به حالت اولیه
# ---------------------------
def _reset_state_to_defaults() -> None:
    """بازگردانی همه تنظیمات به مقادیر پیش‌فرض (بدون استفاده از فایل text.txt)."""

    # اسپمر
    spammer_config.update({
        "text_caption": "",
        "time": 10,
        "run_spammer": False,
        "run_kill": False,
        "typing_on": False,
        "targets": [],  
    })

    # منشن
    mention_config.update({
        "textMen": "",
        "useridMen": "",
        "is_menshen": False,
        "group_menshen": False,
        "group_ids": [],
    })

    # دشمن‌ها
    enemy_config.update({
        "enemy": [],
        "special_enemy": [],
        "enemy_ignore": 0,
        "enemy_counter": {},
        "mute": [],
        "specialenemytext": [],
        "SPTimelist": [],
    })

    # ادمین‌ها
    admin_config.update({"admins": AllConfig["owners"]})

    # تغییر نام
    names_config.update({
        "names": [],
        "change_interval_h": 1,
        "changenames": False,
        "changenames_idx": 0,
        "changenames_task": None,
    })

    # بکاپ
    backup_config.update({
        "bk_enabled": True,
        "bk_db": "downloads/backup.db",
        "bk_dir": "downloads/bk_exports",
        "bk_wipe_threshold": 10,
        "bk_wipe_window_minutes": 1,
        "bk_cooldown_minutes": 1,
    })

    # مدیا
    media_config.update({"catch_view_once": True})

    # تایمر
    timer_config.update({
        "text": "",
        "time": 0,
        "chat_id": None,
        "first_time": None,
        "last_interval": 0,
        "repeat": 100,
        "message_ids": [],
        "is_running": False,
        "auto": False,
        "targets": [],  
    })

    # متن‌ها (پاک‌سازی لیست)
    text_config.update({
        "lines": [],
        "caption":"",
    })

    AllConfig.update({
        "app": app_config,
        "spammer": spammer_config,
        "mention": mention_config,
        "enemy": enemy_config,
        "admin": admin_config,
        "names": names_config,
        "backup": backup_config,
        "media": media_config,
        "timer": timer_config,
        "text": text_config,
    })
