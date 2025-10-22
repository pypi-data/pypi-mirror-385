from pyrogram.types import Message

async def _edit_or_reply(message: Message, text: str, **kwargs):
    """
    سعی می‌کند پیام فعلی را ویرایش کند؛ اگر نشد، ریپلای می‌فرستد.
    kwargs مثل disable_web_page_preview یا parse_mode را پاس بده.
    """
    try: 
        await message.edit_text(text, **kwargs)
    except Exception: 
        await message.reply(text, **kwargs)
