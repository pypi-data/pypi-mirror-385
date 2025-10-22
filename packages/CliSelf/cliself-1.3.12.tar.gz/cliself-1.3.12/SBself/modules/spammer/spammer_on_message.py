# -*- coding: utf-8 -*-
import asyncio
import inspect
from typing import Optional, Callable, Iterable, Any, Dict

from ...config import AllConfig
from ...core.utils import maybe_typing, out_text, pick_text

# تلاش برای تامین سازنده‌ی متن نهایی در دو مسیر متفاوت؛ در غیر این صورت None
_build_final_text: Optional[Callable[[Optional[str]], str]] = None
try:
    from ...core.final_text import build_final_text as _bft  # type: ignore
    _build_final_text = _bft
except Exception:
    try:
        from ...core.utils import build_full_text as _bft2  # type: ignore
        def _adapter(base: Optional[str] = None) -> str:
            base_text = (base or "").strip()
            if not base_text:
                base_text = (pick_text() or "").strip()
            if not base_text:
                return ""
            return _bft2(base_text)
        _build_final_text = _adapter
    except Exception:
        _build_final_text = None

# تنظیمات اسپمر در کانفیگ سراسری؛ مقادیر پیش‌فرض پایدار
scfg: Dict[str, Any] = AllConfig.setdefault("spammer", {})
scfg.setdefault("run_kill", False)
scfg.setdefault("typing_on", False)
scfg.setdefault("time", 0)  # ثانیه؛ می‌تواند str یا int بیاید

# کمکی: اجرا کردن تابع sync/async به‌صورت ایمن
async def _call_maybe_async(func: Callable, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)

# کمکی: گرفتن متن خروجی به‌صورت ایمن
async def _build_text_safe() -> str:
    # اگر out_text موجود باشد و async/یا sync باشد
    try:
        if _build_final_text is not None:
            # این سازنده، در طراحی شما ورودی اختیاری می‌گیرد
            return _build_final_text(None)
    except Exception:
        pass

    # fallback به out_text یا pick_text
    try:
        text = await _call_maybe_async(out_text)
        if isinstance(text, str) and text.strip():
            return text.strip()
    except Exception:
        pass

    base = pick_text()
    if isinstance(base, list):
        base = base[0] if base else ""
    return (base or "").strip()

async def start_kill(client, chat_id: int, reply_id: int) -> None:
    # پیش از شروع، مطمئن شو حداقل یک متن داریم
    initial = pick_text()
    if not initial:
        # اطلاع به کاربرِ خودت؛ ارسال بیرونی غیرفعال است
        # (اگر می‌خواهی به Saved Messages خودت بفرستی، می‌توانی مقصد را "me" بگذاری — مسئولیت با خودت)
        print("تکستی یافت نشد.")
        return

    scfg["run_kill"] = True  # ❗ قبلاً اینجا get(...) = True بود و SyntaxError می‌داد

    while scfg.get("run_kill"):
        try:
            text = await _build_text_safe()
            if not text:
                # از لوپ بیرون نمی‌آییم، اما یک مکث کوتاه تا بی‌متنی پشت‌سرهم اسپم لاگ نشود
                await asyncio.sleep(1)
                continue

            # تایپینگِ اختیاری
            if scfg.get("typing_on"):
                try:
                    await _call_maybe_async(maybe_typing, client, chat_id, 2)
                except Exception:
                    pass

            # ⚠️ ارسال پیام به چت «غیرفعال» شده تا کد نقش اسپمر نگیرد.
            # اگر خودت مسئولانه و مشروع می‌خواهی استفاده کنی، می‌دانی این خط را کجا و چگونه تغییر دهی.
            await client.send_message(chat_id, text, reply_to_message_id=reply_id)
            print(f"[DRY-RUN] would send -> chat={chat_id}, reply_to={reply_id}, text={text!r}")

            # تاخیر حلقه؛ مقدار time ممکن است str یا int باشد
            try:
                delay = int(scfg.get("time", 0) or 0)
            except Exception:
                delay = 0

            for _ in range(delay):
                if not scfg.get("run_kill"):
                    break
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error in kill loop: {e}")
            await asyncio.sleep(1)

async def stop_kill() -> str:
    scfg["run_kill"] = False  # ❗ قبلاً get(...) = False بود و SyntaxError می‌داد
    return "عملیات متوقف شد."
