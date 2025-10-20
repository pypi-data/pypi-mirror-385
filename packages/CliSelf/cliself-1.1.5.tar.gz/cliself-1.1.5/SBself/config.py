# -*- coding: utf-8 -*-
# File: SBself/config.py

import os

# ---------------------------
# 👥 لیست ادمین‌ها
# ---------------------------
adminList = []


# ---------------------------
# 🧠 تنظیمات کلی اپلیکیشن
# ---------------------------
app_config = {
    "name": "app",
    "api_id": 17221354,
    "api_hash": "b86bbf4b700b4e922fff2c05b3b8985f",
    "number": "+989145036505",
}


# ---------------------------
# 💬 اسپمر و پیام‌رسانی خودکار
# ---------------------------
spammer_config = {
    "text_caption": "",
    "time": 10,
    "run_spammer": False,
    "run_kill": False,
    "typing_on": False,
}


# ---------------------------
# 🧍‍♂️ تنظیمات منشن‌ها
# ---------------------------
mention_config = {
    "textMen": "",
    "useridMen": "",
    "is_menshen": False,
    "group_menshen": False,
    "group_ids": [],
}


# ---------------------------
# 😡 دشمن‌ها و mute
# ---------------------------
enemy_config = {
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
admin_config = {
    "admins": [],
}


# ---------------------------
# 📝 تغییر نام خودکار
# ---------------------------
names_config = {
    "names": [],
    "change_interval_h": 1,
    "changenames": False,
    "changenames_idx": 0,
    "changenames_task": None,
}


# ---------------------------
# 💾 بکاپ و پایگاه داده
# ---------------------------
backup_config = {
    "bk_enabled": True,
    "bk_db": "downloads/backup.db",
    "bk_dir": "downloads/bk_exports",
    "bk_wipe_threshold": 50,
}


# ---------------------------
# 📷 تنظیمات مدیا
# ---------------------------
media_config = {
    "catch_view_once": True,
}


# ---------------------------
# ⏱ تایمر پیام‌ها
# ---------------------------
timer_config = {
    "text": "",
    "time": 0,
    "chat_id": None,
    "first_time": None,
    "last_interval": 0,
    "repeat": 100,
    "message_ids": [],
    "is_running": False,
    "auto":False,
}


# ---------------------------
# ⚙️ ترکیب همه‌ی تنظیمات در AllConfig
# ---------------------------
AllConfig = {
    "app": app_config,
    "spammer": spammer_config,
    "mention": mention_config,
    "enemy": enemy_config,
    "admin": admin_config,
    "names": names_config,
    "backup": backup_config,
    "media": media_config,
    "timer": timer_config,
}


# ---------------------------
# 🔁 تابع ریست تنظیمات به حالت اولیه
# ---------------------------
def _reset_state_to_defaults():
    """بازگردانی همه تنظیمات به مقادیر پیش‌فرض"""
    # اسپمر
    spammer_config.update({
        "text_caption": "",
        "time": 10,
        "run_spammer": False,
        "run_kill": False,
        "typing_on": False,
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
    admin_config.update({"admins": adminList})

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
        "bk_wipe_threshold": 50,
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
        "auto":False,
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
    })

    # بازنشانی فایل text.txt
    os.makedirs("downloads", exist_ok=True)
    with open("downloads/text.txt", "w", encoding="utf-8") as f:
        f.write("")
