from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

marker = "    async def _send(self, job: Job, roast: str) -> None:"

new_func = '''    async def _send_saved_media(self, job: Job, roast: str) -> bool:
        bot = self.application.bot
        memory = self.media_memory

        kinds = []

        if memory.count("photos"):
            kinds.append("photos")

        if memory.count("gifs"):
            kinds.append("gifs")

        if memory.count("stickers"):
            kinds.append("stickers")

        if memory.count("voices"):
            kinds.append("voices")

        if not kinds:
            return False

        kind = random.choice(kinds)
        file_id = memory.random(kind)

        if not file_id:
            return False

        try:
            if kind == "photos":
                await bot.send_photo(
                    chat_id=job.chat_id,
                    photo=file_id,
                    caption=roast,
                    reply_to_message_id=job.message_id,
                )

            elif kind == "gifs":
                await bot.send_animation(
                    chat_id=job.chat_id,
                    animation=file_id,
                    caption=roast,
                    reply_to_message_id=job.message_id,
                )

            elif kind == "stickers":
                await bot.send_sticker(
                    chat_id=job.chat_id,
                    sticker=file_id,
                )
                await bot.send_message(
                    chat_id=job.chat_id,
                    text=roast,
                    reply_to_message_id=job.message_id,
                )

            elif kind == "voices":
                await bot.send_voice(
                    chat_id=job.chat_id,
                    voice=file_id,
                    reply_to_message_id=job.message_id,
                )
                await bot.send_message(
                    chat_id=job.chat_id,
                    text=roast,
                    reply_to_message_id=job.message_id,
                )

            logger.info("Отправлено сохранённое медиа: %s", kind)
            return True

        except (BadRequest, TimedOut, NetworkError, TelegramError) as exc:
            logger.warning("Не удалось отправить сохранённое медиа %s: %s", kind, exc)
            return False


'''

if "_send_saved_media" not in s:
    if marker not in s:
        raise SystemExit("_send не найден")
    s = s.replace(marker, new_func + marker, 1)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: функция сохранённых медиа добавлена")