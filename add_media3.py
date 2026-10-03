from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

marker = "async def on_text("

new_handlers = '''async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or update.effective_chat.type not in GROUP_TYPES:
        return

    message = update.effective_message
    if not message:
        return

    service = get_service(context)
    if not service:
        return

    if message.photo:
        service.media_memory.add("photos", message.photo[-1].file_id)

    elif message.animation:
        service.media_memory.add("gifs", message.animation.file_id)

    elif message.sticker:
        service.media_memory.add("stickers", message.sticker.file_id)

    elif message.voice:
        service.media_memory.add("voices", message.voice.file_id)


'''

if "async def on_media(" not in s:
    if marker not in s:
        raise SystemExit("on_text не найден")
    s = s.replace(marker, new_handlers + marker, 1)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: сохранение медиа добавлено")