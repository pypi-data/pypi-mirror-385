# -*- coding: utf-8 -*-
# File: SBself/modules/spammer/spammer.py
#
# اسپمر Threading با پشتیبانی همزمان از کلاینت‌های sync/async
# فیکس مهم: هندلِ «Invalid parse mode» با تلاش‌های چندمرحله‌ای برای تعیین parse_mode
# - اول تلاش با pyrogram.enums.ParseMode.HTML
# - بعد "HTML"
# - بعد "html"
# - و در نهایت بدون parse_mode (فقط برای اینکه پیام از دست نرود)
#
# باقی ویژگی‌ها:
# - توقف سریع با threading.Event
# - قفل RLock برای ایمنی
# - Jitter سبک
# - مونتاژ متن نهایی از core/final_text.build_final_text یا utils.build_full_text
# - optional typing_on
#
# پیش‌نیازهای کانفیگ:
#   AllConfig["spammer"] = {
#       "targets": [ ... ],
#       "time": 10,
#       "typing_on": False,
#   }
#   AllConfig["text"]["lines"]  → لیست متن‌های رندوم
#   AllConfig["mention"] → textMen/is_menshen/group_menshen/group_ids/useridMen
#
from __future__ import annotations

import time
import threading
import random
import asyncio
import inspect
from typing import List, Optional, Callable, Dict, Any

from ...config import AllConfig

# انتخاب بهترین بیلدر متن نهایی
_build_final_text: Optional[Callable[[str | None], str]] = None
try:
    from ...core.final_text import build_final_text as _bft  # type: ignore
    _build_final_text = _bft
except Exception:
    try:
        from ...core.utils import build_full_text as _bft2  # type: ignore
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
    """حلقه‌ی asyncio در Thread جدا برای اجرای کوروتین‌ها از دنیای Threading."""
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
    # API
    # -----------------------------
    def start(self, client) -> None:
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
        with self._lock:
            AllConfig.setdefault("spammer", {})["targets"] = list(targets)
            self._targets_cache = list(targets)

    def set_delay(self, seconds: int) -> None:
        seconds = max(self._MIN_DELAY_SEC, int(seconds or 0))
        with self._lock:
            AllConfig.setdefault("spammer", {})["time"] = seconds
            self._delay_cache = seconds

    def set_typing(self, enabled: bool) -> None:
        with self._lock:
            AllConfig.setdefault("spammer", {})["typing_on"] = bool(enabled)
            self._typing_on_cache = bool(enabled)

    # -----------------------------
    # ارسال (sync/async) + هندل parse_mode
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

    def _build_parse_kwargs(self) -> Dict[str, Any]:
        """
        تلاش برای تولید kwargs مناسب parse_mode:
          - اول: pyrogram.enums.ParseMode.HTML
          - دوم: "HTML"
          - سوم: "html"
        """
        # disable_web_page_preview برای تمیزی پیام
        base = {"disable_web_page_preview": True}
        # تلاش با enums.ParseMode.HTML (Pyrogram v2)
        try:
            from pyrogram.enums import ParseMode as _PM  # type: ignore
            return {**base, "parse_mode": _PM.HTML}
        except Exception:
            pass
        # تلاش با رشته‌ی "HTML"
        return {**base, "parse_mode": "HTML"}

    def _send_message_with_best_effort(self, chat_id, text: str) -> None:
        """
        ارسال با چند مرحله تلاش برای parse_mode تا خطای Invalid parse mode ندهد.
        مراحل:
          1) parse_mode = enums.ParseMode.HTML (اگر موجود بود) یا "HTML"
          2) اگر خطای Invalid Parse Mode داد → "html"
          3) اگر باز خطا داد → بدون parse_mode (برای اینکه پیام اصلاً از دست نرود)
        """
        send = getattr(self._client, "send_message", None)
        if not callable(send):
            raise RuntimeError("Client has no send_message()")

        # مرحله 1
        kwargs = self._build_parse_kwargs()
        try:
            if self._client_is_async_send and self._runner:
                self._runner.run(send(chat_id, text, **kwargs), timeout=60.0)
            else:
                send(chat_id, text, **kwargs)
            return
        except Exception as e1:
            msg = str(e1) or ""
            if "Invalid parse mode" not in msg and "parse mode" not in msg.lower():
                # خطای دیگری بوده → دوباره پرتاب
                raise

        # مرحله 2: "html" کوچک
        try:
            alt_kwargs = {k: v for k, v in kwargs.items() if k != "parse_mode"}
            alt_kwargs["parse_mode"] = "html"
            if self._client_is_async_send and self._runner:
                self._runner.run(send(chat_id, text, **alt_kwargs), timeout=60.0)
            else:
                send(chat_id, text, **alt_kwargs)
            return
        except Exception as e2:
            msg2 = str(e2) or ""
            if "Invalid parse mode" not in msg2 and "parse mode" not in msg2.lower():
                raise

        # مرحله 3: بدون parse_mode (آخرین راهکار)
        fallback_kwargs = {k: v for k, v in kwargs.items() if k != "parse_mode"}
        try:
            if self._client_is_async_send and self._runner:
                self._runner.run(send(chat_id, text, **fallback_kwargs), timeout=60.0)
            else:
                send(chat_id, text, **fallback_kwargs)
        except Exception as e3:
            # این یکی دیگر واقعاً بگذاریم لاگ شود
            raise e3

    def _send_message(self, chat_id, text: str) -> None:
        # یک رَپر نازک برای تمیز نگه داشتن call site
        try:
            self._send_message_with_best_effort(chat_id, text)
        except Exception as e:
            logger.warning(f"Send failed to {chat_id}: {e}")

    # -----------------------------
    # لوپ اصلی
    # -----------------------------
    def _run_loop(self, client) -> None:
        if _build_final_text is None:
            logger.error("No text builder available: define core/final_text.build_final_text or utils.build_full_text.")
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

                text = _build_final_text(None)  # None → انتخاب خودکار متن رندوم از کانفیگ
                if not text:
                    if self._stop_evt.wait(timeout=1.0):
                        break
                    self._refresh_cached_config()
                    continue

                for chat_id in targets:
                    if self._stop_evt.is_set():
                        break
                    try:
                        if typing_on:
                            self._send_typing(chat_id)
                    except Exception:
                        pass
                    self._send_message(chat_id, text)
                    if self._stop_evt.wait(timeout=0.15 + random.random() * 0.10):
                        break

                jitter = random.uniform(0.0, min(0.25 * delay, 2.0))
                next_wakeup = time.monotonic() + max(self._MIN_DELAY_SEC, delay) + jitter
                remaining = max(0.0, next_wakeup - time.monotonic())
                if self._stop_evt.wait(timeout=remaining):
                    break
                self._refresh_cached_config()

            except Exception as e:
                logger.error(f"Spammer loop error: {e}")
                if self._stop_evt.wait(timeout=1.0):
                    break
                self._refresh_cached_config()

    # -----------------------------
    # به‌روزرسانی کش
    # -----------------------------
    def _refresh_cached_config_unlocked(self) -> None:
        scfg = AllConfig.setdefault("spammer", {})
        self._targets_cache = list(scfg.setdefault("targets", []))
        self._delay_cache = max(self._MIN_DELAY_SEC, int(scfg.get("time", 10) or 10))
        self._typing_on_cache = bool(scfg.get("typing_on", False))

    def _refresh_cached_config(self) -> None:
        with self._lock:
            self._refresh_cached_config_unlocked()
