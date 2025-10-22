# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer.py
#
# اسپمر بهینه، کم‌مصرف و «بی‌حاشیه» مبتنی بر Threading
# - هماهنگ با کلاینت‌های sync و async (Pyrogram/Telethon و …)
# - توقف سریع با threading.Event (بدون busy-wait)
# - قفل امن برای دسترسی به تنظیمات (RLock)
# - Jitter سبک جهت جلوگیری از Burst و RateLimit
# - مونتاژ متن نهایی از کانفیگ: متن‌های رندوم + کپشن + منشن (HTML)
# - ارسال با parse_mode="html" تا منشن‌های tg://user?id=... درست رندر شوند
#
# پیش‌نیازهای کانفیگ:
#   AllConfig["spammer"] = {
#       "targets": [ ... ],      # لیست chat_id ها
#       "time": 10,              # ثانیه بین ارسال‌ها (حداقل 1)
#       "typing_on": False,      # نمایش "typing..." بین ارسال‌ها
#       "text_caption": "",      # متن کپشن (در صورت استفاده در مونتاژ)
#       "caption_on": False,     # فعال‌سازی صریح کپشن (اختیاری)
#   }
#
# منبع متن:
#   AllConfig["text"]["lines"]  ← لیست رشته‌ها (برای انتخاب تصادفی)
#
# منشن:
#   AllConfig["mention"] با کلیدهای:
#       "is_menshen", "useridMen", "group_menshen", "group_ids", "textMen"
#
# نکته: اگر فایل SBself/core/final_text.py دارید، از build_final_text استفاده می‌شود.
# در غیر این‌صورت از SBself/core/utils.py و تابع build_full_text استفاده خواهد شد.

from __future__ import annotations

import time
import threading
import random
import asyncio
import inspect
from typing import List, Optional, Callable

from ...config import AllConfig

# -- تشخیص بهترین تابع برای ساخت «متن نهایی»
_build_final_text: Optional[Callable[[str | None], str]] = None
try:
    # ترجیح: ماژول اختصاصی final_text (اگر موجود باشد)
    from ...core.final_text import build_final_text as _bft  # type: ignore
    _build_final_text = _bft
except Exception:
    try:
        # fallback: util قدیمی
        from ...core.utils import build_full_text as _bft2  # type: ignore
        # یک آداپتر کوچک تا امضای سازگار داشته باشد
        def _adapter(base: Optional[str] = None) -> str:
            from ...core.utils import pick_text  # type: ignore
            base_text = (base or "").strip()
            if not base_text:
                base_text = (pick_text() or "").strip()
            if not base_text:
                return ""
            return _bft2(base_text)
        _build_final_text = _adapter
    except Exception:
        _build_final_text = None

try:
    from ...core.logger import get_logger
    logger = get_logger("spammer_threaded")
except Exception:
    import logging
    logger = logging.getLogger("spammer_threaded")


class _AsyncLoopRunner:
    """
    حلقه‌ی asyncio در یک Thread جدا برای اجرای ایمن کوروتین‌ها
    وقتی کلاینت (Pyrogram/Telethon) async باشد و ما Threading داریم.
    """
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
                    pending = asyncio.all_tasks(loop=self._loop)  # Py3.10 سازگار
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
    اسپمر مبتنی بر Thread که متن نهایی (رندوم + کپشن + منشن) را می‌سازد و ارسال می‌کند.
    """

    _MIN_DELAY_SEC = 1

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._lock = threading.RLock()
        self._running = False

        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache: List[int] = list(scfg.setdefault("targets", []))
        self._delay_cache: int = max(1, int(scfg.get("time", 10) or 10))
        self._typing_on_cache: bool = bool(scfg.get("typing_on", False))

        self._client = None
        self._runner: Optional[_AsyncLoopRunner] = None
        self._client_is_async_send = False
        self._client_is_async_action = False

    # -----------------------------
    # API عمومی
    # -----------------------------
    def start(self, client) -> None:
        """
        آغاز اسپمر. اگر کلاینت async باشد، یک event loop جداگانه راه‌اندازی می‌کند.
        """
        with self._lock:
            if self._running:
                logger.info("Spammer already running; ignoring start().")
                return

            self._client = client
            send = getattr(client, "send_message", None)
            act = getattr(client, "send_chat_action", None)
            self._client_is_async_send = inspect.iscoroutinefunction(send)
            self._client_is_async_action = inspect.iscoroutinefunction(act)

            if self._client_is_async_send or self._client_is_async_action:
                self._runner = _AsyncLoopRunner()
                self._runner.start()

            self._refresh_cached_config_unlocked()
            self._stop_evt.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                args=(client,),
                name="SpammerThread",
                daemon=True,
            )
            self._running = True
            self._thread.start()
            logger.info("Spammer started.")

    def stop(self) -> None:
        """توقف تمیز و سریع اسپمر."""
        with self._lock:
            if not self._running:
                return
            self._stop_evt.set()
            thread = self._thread

        if thread and thread.is_alive():
            thread.join(timeout=5.0)

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

    def set_typing(self, enabled: bool) -> None:
        """فعال/غیرفعال کردن نمایش typing (Thread-safe)."""
        with self._lock:
            AllConfig.setdefault("spammer", {})["typing_on"] = bool(enabled)
            self._typing_on_cache = bool(enabled)

    # -----------------------------
    # ارسال (sync/async)
    # -----------------------------
    def _send_typing(self, chat_id) -> None:
        if not self._typing_on_cache:
            return
        act = getattr(self._client, "send_chat_action", None)
        if not callable(act):
            return
        try:
            if self._client_is_async_action and self._runner:
                self._runner.run(act(chat_id, "typing"), timeout=10.0)
            else:
                act(chat_id, "typing")
        except Exception:
            pass  # اختیاری

    def _send_message(self, chat_id, text: str) -> None:
        send = getattr(self._client, "send_message", None)
        if not callable(send):
            raise RuntimeError("Client has no send_message()")
        # مهم: parse_mode="html" برای رندر صحیح منشن‌ها
        kwargs = {"parse_mode": "html", "disable_web_page_preview": True}
        if self._client_is_async_send and self._runner:
            self._runner.run(send(chat_id, text, **kwargs), timeout=60.0)
        else:
            send(chat_id, text, **kwargs)

    # -----------------------------
    # لوپ اصلی
    # -----------------------------
    def _run_loop(self, client) -> None:
        """
        حلقه‌ی کار:
          1) خواندن کش تنظیمات
          2) ساخت متن نهایی
          3) ارسال به تمام تارگت‌ها (با فاصله‌ی کوتاه)
          4) خواب بر اساس delay + jitter
        """
        if _build_final_text is None:
            logger.error("No text builder available: final_text.build_final_text or utils.build_full_text not found.")
            return

        next_wakeup = time.monotonic()
        while not self._stop_evt.is_set():
            try:
                with self._lock:
                    targets = list(self._targets_cache)
                    delay = self._delay_cache
                    typing_on = self._typing_on_cache

                if not targets:
                    if self._stop_evt.wait(timeout=2.0):
                        break
                    self._refresh_cached_config()
                    continue

                # ساخت متن نهایی (ممکن است از لیست کانفیگ متن تصادفی انتخاب کند)
                text = _build_final_text(None)  # None → انتخاب خودکار متن
                if not text:
                    if self._stop_evt.wait(timeout=1.0):
                        break
                    self._refresh_cached_config()
                    continue

                # ارسال به همه‌ی تارگت‌ها
                for chat_id in targets:
                    if self._stop_evt.is_set():
                        break
                    try:
                        if typing_on:
                            self._send_typing(chat_id)
                    except Exception:
                        pass
                    try:
                        self._send_message(chat_id, text)
                    except Exception as e:
                        logger.warning(f"Send failed to {chat_id}: {e}")
                    # مکث کوتاه بین تارگت‌ها برای جلوگیری از Burst
                    if self._stop_evt.wait(timeout=0.15 + random.random() * 0.10):
                        break

                # زمان اجرای بعدی با jitter سبک
                jitter = random.uniform(0.0, min(0.25 * delay, 2.0))
                next_wakeup = time.monotonic() + max(self._MIN_DELAY_SEC, delay) + jitter

                # خواب کارا و امکان توقف فوری
                remaining = max(0.0, next_wakeup - time.monotonic())
                if self._stop_evt.wait(timeout=remaining):
                    break

                # بروزرسانی کش
                self._refresh_cached_config()

            except Exception as e:
                logger.error(f"Spammer loop error: {e}")
                if self._stop_evt.wait(timeout=1.0):
                    break
                self._refresh_cached_config()

    # -----------------------------
    # به‌روزرسانی کش تنظیمات
    # -----------------------------
    def _refresh_cached_config_unlocked(self) -> None:
        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache = list(scfg.setdefault("targets", []))
        self._delay_cache = max(self._MIN_DELAY_SEC, int(scfg.get("time", 10) or 10))
        self._typing_on_cache = bool(scfg.get("typing_on", False))

    def _refresh_cached_config(self) -> None:
        with self._lock:
            self._refresh_cached_config_unlocked()
