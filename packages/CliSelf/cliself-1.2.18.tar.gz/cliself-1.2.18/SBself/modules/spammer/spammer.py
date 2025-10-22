# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer.py
#
# نسخه‌ی بهینه و کم‌مصرف مبتنی بر Threading
# - بدون asyncio
# - توقف سریع با threading.Event
# - قفل برای خواندن/نوشتن امن تنظیمات
# - ارسال منظم با دقت زمانی بالا و Jitter سبک برای پخش بار
# - بدون وابستگی به فایل text.txt (متن‌ها از AllConfig["text"]["lines"])
#
# نکته: اگر کلاینت شما متد sync برای send_message ندارد، یک
# رَپرِ همگام (sync wrapper) بسازید که در حلقه‌ی event-loop خودش await کند.
# در اینجا فرض شده client.send_message قابل فراخوانیِ همگام است.

from __future__ import annotations

import time
import threading
import random
from typing import List, Optional

from ...config import AllConfig
from ...core.final_text import build_final_text

try:
    from ...core.logger import get_logger
    logger = get_logger("spammer_threaded")
except Exception:
    import logging
    logger = logging.getLogger("spammer_threaded")


class Spammer:
    """
    اسپمر مبتنی بر Thread که متن نهایی را (رندوم + کپشن + منشن) می‌سازد و
    به تارگت‌ها می‌فرستد.

    تنظیمات:
      - AllConfig["spammer"]["targets"] : List[int]
      - AllConfig["spammer"]["time"]    : int (ثانیه بین ارسال‌ها)
      - متن‌ها در AllConfig["text"]["lines"] نگهداری می‌شوند.
    """

    # حداقل تاخیر بین ارسال‌ها برای جلوگیری از مصرف بیش از حد CPU/RateLimit
    _MIN_DELAY_SEC = 1

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._lock = threading.RLock()
        self._running = False
        # کشِ سبک برای جلوگیری از دسترسی مداوم به AllConfig
        self._targets_cache: List[int] = AllConfig["spammer"]["targets"]
        self._delay_cache: int = AllConfig["spammer"]["time"]

    # -----------------------------
    # API عمومی
    # -----------------------------
    def start(self, client) -> None:
        """شروع اسپمر (ایمن در برابر دوبار start)."""
        with self._lock:
            if self._running:
                logger.info("Spammer already running; ignoring start().")
                return
            self._refresh_cached_config_unlocked()
            self._stop_evt.clear()
            self._thread = threading.Thread(
                target=self._run_loop(client),
                name="SpammerThread",
                args=(client,),
                daemon=True,
            )
            self._running = True
            self._thread.start()
            logger.info("Spammer started.")

    def stop(self) -> None:
        """توقف تمیز و سریع با Event."""
        with self._lock:
            if not self._running:
                return
            self._stop_evt.set()
            thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=5.0)
        with self._lock:
            self._thread = None
            self._running = False
            logger.info("Spammer stopped.")

    def is_running(self) -> bool:
        return self._running

    def set_targets(self, targets: List[int]) -> None:
        """بروزرسانی تارگت‌ها در حین اجرا (Thread-safe)."""
        with self._lock:
            AllConfig.setdefault("spammer", {})["targets"] = list(targets)
            self._targets_cache = list(targets)

    def set_delay(self, seconds: int) -> None:
        """بروزرسانی تاخیر پایه (Thread-safe)."""
        seconds = max(self._MIN_DELAY_SEC, int(seconds or 0))
        with self._lock:
            AllConfig.setdefault("spammer", {})["time"] = seconds
            self._delay_cache = seconds

    # -----------------------------
    # هسته‌ی اسپمر
    # -----------------------------
    def _run_loop(self, client) -> None:
        """
        حلقه‌ی اصلی:
          - متن نهایی را یک بار در هر چرخه می‌سازد
          - به همه‌ی تارگت‌ها می‌فرستد
          - با رعایت تاخیر (به‌همراه jitter سبک) sleep می‌کند
          - توقف سریع با Event.wait
        """
        # هدف: مصرف CPU پایین؛ فقط در زمان‌های لازم کار کنیم.
        next_wakeup = time.monotonic()
        while not self._stop_evt.is_set():
            try:
                # همگام‌سازی خوانش تنظیمات
                with self._lock:
                    targets = list(self._targets_cache)
                    delay = self._delay_cache

                if not targets:
                    # اگر تارگتی نیست، دیرتر چک کنیم
                    if self._stop_evt.wait(timeout=2.0):
                        break
                    # تلاش دوباره برای سینک تنظیمات
                    self._refresh_cached_config()
                    continue

                # ساخت متن نهایی
                text = build_final_text()
                if not text:
                    # اگر متنی نداشتیم، کمی صبر و تنظیمات را دوباره چک کنیم
                    if self._stop_evt.wait(timeout=1.0):
                        break
                    self._refresh_cached_config()
                    continue

                # ارسال به همه‌ی تارگت‌ها
                for chat_id in targets:
                    if self._stop_evt.is_set():
                        break

                    # تلاش برای ارسال typing اگر کلاینت پشتیبانی کند (non-blocking best-effort)
                    try:
                        send_chat_action = getattr(client, "send_chat_action", None)
                        if callable(send_chat_action):
                            send_chat_action(chat_id, "typing")
                    except Exception:
                        pass  # تایپینگ اختیاری‌ست؛ خطایش حیاتی نیست

                    try:
                        client.send_message(chat_id, text)
                    except Exception as e:
                        # خطا را لاگ می‌کنیم اما حلقه را متوقف نمی‌کنیم
                        logger.warning(f"Send failed to {chat_id}: {e}")

                    # بین تارگت‌ها یک مکث کوتاه تصادفی برای کاهش Bursting
                    if self._stop_evt.wait(timeout=0.15 + random.random() * 0.10):
                        break

                # محاسبه‌ی بیدار شدن بعدی: delay + jitter سبک
                jitter = random.uniform(0.0, min(0.25 * delay, 2.0))
                next_wakeup = time.monotonic() + max(self._MIN_DELAY_SEC, delay) + jitter

                # خواب کارا: Event.wait تا بتوانیم سریع stop کنیم
                remaining = max(0.0, next_wakeup - time.monotonic())
                if self._stop_evt.wait(timeout=remaining):
                    break

                # هر چرخه یک‌بار تنظیمات را بروز می‌کنیم
                self._refresh_cached_config()

            except Exception as e:
                # هیچ‌گاه حلقه را با خطا نمی‌کشیم؛ کمی صبر و تلاش مجدد
                logger.error(f"Spammer loop error: {e}")
                if self._stop_evt.wait(timeout=1.0):
                    break
                self._refresh_cached_config()

    # -----------------------------
    # خواندن تنظیمات به‌صورت Thread-safe
    # -----------------------------
    def _refresh_cached_config_unlocked(self) -> None:
        """فقط در حالتی که lock گرفته‌ایم صدا شود."""
        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache = list(scfg.setdefault("targets", []))
        self._delay_cache = max(self._MIN_DELAY_SEC, int(scfg.get("time", 10) or 10))

    def _refresh_cached_config(self) -> None:
        with self._lock:
            self._refresh_cached_config_unlocked()
