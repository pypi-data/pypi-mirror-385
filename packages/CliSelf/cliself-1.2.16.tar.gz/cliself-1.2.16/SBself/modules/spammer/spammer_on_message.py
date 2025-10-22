import asyncio
from ...config import AllConfig
from ...core.utils import maybe_typing,out_text,pick_text

async def start_kill(client, chat_id: int, reply_id: int) -> None:
    lines = pick_text()
    if not lines:
        await client.send_message(chat_id, "تکستی یافت نشد.")
        return

    AllConfig["run_kill"] = True

    while AllConfig["run_kill"]:
        try:
            text = await out_text()
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
