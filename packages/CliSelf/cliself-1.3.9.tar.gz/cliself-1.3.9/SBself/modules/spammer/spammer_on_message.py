import asyncio
from ...config import AllConfig
from ...core.utils import maybe_typing,out_text,pick_text
from typing import List, Optional, Callable, Dict, Any
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

async def start_kill(client, chat_id: int, reply_id: int) -> None:
    lines = pick_text()
    if not lines:
        await client.send_message(chat_id, "تکستی یافت نشد.")
        return

    AllConfig["run_kill"] = True

    while AllConfig["run_kill"]:
        try:
            text = _build_final_text(None)
            if AllConfig["typing_on"]:
                await maybe_typing(client, chat_id, 2)
            await client.send_message(chat_id, text, reply_to_message_id=reply_id)

            for _ in range(int(AllConfig["time"])):
                if not AllConfig["run_kill"]:
                    break
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error in kill loop: {e}")
            await asyncio.sleep(1)


async def stop_kill() -> str:
    AllConfig["run_kill"] = False
    return "عملیات متوقف شد."
