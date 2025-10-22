# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer.py
#
# نسخه‌ی بهینه و کم‌مصرف مبتنی بر Threading — با پشتیبانی از کلاینت‌های async
# - بدون asyncio در API اسپمر (اما پشت‌صحنه اگر کلاینت async باشد، از حلقه‌ی جدا استفاده می‌کنیم)
# - توقف سریع با threading.Event
# - قفل برای خواندن/نوشتن امن تنظیمات
# - ارسال منظم + Jitter سبک
# - متن‌ها از AllConfig["text"]["lines"]
# - سازگار با Pyrogram/Telethon (async) و کلاینت‌های sync

from __future__ import annotations

import time
import threading
import random
import asyncio
import inspect
from typing import List, Optional

from ...config import AllConfig
from ...core.final_text import build_final_text

try:
    from ...core.logger import get_logger
    logger = get_logger("spammer_threaded")
except Exception:
    import logging
    logger = logging.getLogger("spammer_threaded")


class _AsyncLoopRunner:
    """حلقه‌ی asyncio در یک Thread جدا برای اجرای کوروتین‌ها به‌صورت همگام از Thread اسپمر."""
    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._started = threading.Event()

    def start(self) -> None:
        if self._loop and self._loop.is_running():
            return

        def _target():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._started.set()
            try:
                self._loop.run_forever()
            finally:
                try:
                    pending = asyncio.all_tasks(loop=self._loop)
                except TypeError:
                    pending = asyncio.all_tasks()
                for t in pending:
                    t.cancel()
                try:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                self._loop.close()

        self._thread = threading.Thread(target=_target, name="SpammerAsyncLoop", daemon=True)
        self._thread.start()
        self._started.wait(timeout=5.0)

    def run(self, coro, timeout: Optional[float] = None):
        """کوروتین را اجرا کن و نتیجه را همگام بگیر."""
        if not self._loop or not self._loop.is_running():
            self.start()
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout=timeout)

    def stop(self) -> None:
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._loop = None
        self._thread = None
        self._started.clear()


class Spammer:
    """
    اسپمر مبتنی بر Thread که متن نهایی را (رندوم + کپشن + منشن) می‌سازد و به تارگت‌ها می‌فرستد.

    تنظیمات:
      - AllConfig["spammer"]["targets"] : List[int]
      - AllConfig["spammer"]["time"]    : int (ثانیه بین ارسال‌ها)
      - متن‌ها در AllConfig["text"]["lines"] نگهداری می‌شوند.
    """

    _MIN_DELAY_SEC = 1

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._lock = threading.RLock()
        self._running = False

        # کش کانفیگ
        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache: List[int] = list(scfg.setdefault("targets", []))
        self._delay_cache: int = int(scfg.get("time", 10) or 10)

        # کلاینت و AsyncRunner (فقط اگر لازم شود)
        self._client = None
        self._runner: Optional[_AsyncLoopRunner] = None
        self._client_is_async_send = False
        self._client_is_async_action = False

    # -----------------------------
    # API عمومی
    # -----------------------------
    def start(self, client) -> None:
        """شروع اسپمر (ایمن در برابر دوبار start)."""
        with self._lock:
            if self._running:
                logger.info("Spammer already running; ignoring start().")
                return

            self._client = client
            # تشخیص async بودن متدها
            send = getattr(client, "send_message", None)
            act = getattr(client, "send_chat_action", None)
            self._client_is_async_send = inspect.iscoroutinefunction(send)
            self._client_is_async_action = inspect.iscoroutinefunction(act)

            # اگر async است، حلقه‌ی جدا راه بیندازیم
            if self._client_is_async_send or self._client_is_async_action:
                self._runner = _AsyncLoopRunner()
                self._runner.start()

            self._refresh_cached_config_unlocked()
            self._stop_evt.clear()
            self._thread = threading.Thread(
                target=self._run_loop,          # ✅ تابع را پاس می‌دهیم، نه اجرای آن
                args=(client,),
                name="SpammerThread",
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

        # حلقه‌ی async را هم ببندیم اگر ساخته‌ایم
        with self._lock:
            if self._runner:
                try:
                    self._runner.stop()
                except Exception:
                    pass
                self._runner = None

            self._thread = None
            self._running = False
            self._client = None
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
    def _send_typing(self, chat_id) -> None:
        """ارسال typing به‌صورت sync یا async بسته به نوع کلاینت."""
        act = getattr(self._client, "send_chat_action", None)
        if not callable(act):
            return
        try:
            if self._client_is_async_action and self._runner:
                self._runner.run(act(chat_id, "typing"), timeout=10.0)
            else:
                act(chat_id, "typing")
        except Exception:
            pass  # غیرحیاتی

    def _send_message(self, chat_id, text: str) -> None:
        """ارسال پیام به‌صورت sync یا async بسته به نوع کلاینت."""
        send = getattr(self._client, "send_message", None)
        if not callable(send):
            raise RuntimeError("Client has no send_message()")
        if self._client_is_async_send and self._runner:
            self._runner.run(send(chat_id, text), timeout=60.0)
        else:
            send(chat_id, text)

    def _run_loop(self, client) -> None:
        """
        حلقه‌ی اصلی:
          - متن نهایی را یک بار در هر چرخه می‌سازد
          - به همه‌ی تارگت‌ها می‌فرستد
          - با رعایت تاخیر (به‌همراه jitter سبک) sleep می‌کند
          - توقف سریع با Event.wait
        """
        next_wakeup = time.monotonic()
        while not self._stop_evt.is_set():
            try:
                # همگام‌سازی خوانش تنظیمات
                with self._lock:
                    targets = list(self._targets_cache)
                    delay = self._delay_cache

                if not targets:
                    if self._stop_evt.wait(timeout=2.0):
                        break
                    self._refresh_cached_config()
                    continue

                # ساخت متن نهایی
                text = build_final_text()
                if not text:
                    if self._stop_evt.wait(timeout=1.0):
                        break
                    self._refresh_cached_config()
                    continue

                # ارسال به همه‌ی تارگت‌ها
                for chat_id in targets:
                    if self._stop_evt.is_set():
                        break
                    # typing اختیاری
                    try:
                        self._send_typing(chat_id)
                    except Exception:
                        pass
                    # ارسال پیام
                    try:
                        self._send_message(chat_id, text)
                    except Exception as e:
                        logger.warning(f"Send failed to {chat_id}: {e}")

                    # مکث کوتاه برای پخش بار
                    if self._stop_evt.wait(timeout=0.15 + random.random() * 0.10):
                        break

                # محاسبه‌ی زمان بیداری بعدی
                jitter = random.uniform(0.0, min(0.25 * delay, 2.0))
                next_wakeup = time.monotonic() + max(self._MIN_DELAY_SEC, delay) + jitter

                # خواب کارا
                remaining = max(0.0, next_wakeup - time.monotonic())
                if self._stop_evt.wait(timeout=remaining):
                    break

                # بروز کردن کش
                self._refresh_cached_config()

            except Exception as e:
                logger.error(f"Spammer loop error: {e}")
                if self._stop_evt.wait(timeout=1.0):
                    break
                self._refresh_cached_config()

    # -----------------------------
    # خواندن تنظیمات به‌صورت Thread-safe
    # -----------------------------
    def _refresh_cached_config_unlocked(self) -> None:
        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache = list(scfg.setdefault("targets", []))
        self._delay_cache = max(self._MIN_DELAY_SEC, int(scfg.get("time", 10) or 10))

    def _refresh_cached_config(self) -> None:
        with self._lock:
            self._refresh_cached_config_unlocked()
