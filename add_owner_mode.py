import shutil
from pathlib import Path


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"[{name}] не нашёл ровно одно совпадение. Ничего не изменено.")
    return text.replace(old, new, 1)


config_path = Path("config.py")
ai_path = Path("ai.py")
bot_path = Path("bot.py")

config = config_path.read_text(encoding="utf-8")
ai = ai_path.read_text(encoding="utf-8")
bot = bot_path.read_text(encoding="utf-8")

if "is_owner: bool = False" not in bot:
    raise SystemExit("Сначала выполните fix_owner.py (в bot.py нет поля is_owner).")
if "personality_owner_file" in config:
    raise SystemExit("Похоже, режим владельца уже добавлен.")

# ---------- config.py ----------
config = replace_once(
    config,
    "    personality_file: Path\n",
    "    personality_file: Path\n    personality_owner_file: Path\n",
    "config: поле в Settings",
)

config = replace_once(
    config,
    '    log_level = _env_str("LOG_LEVEL", "INFO").upper()\n',
    '''    personality_owner_file = _env_path("PERSONALITY_OWNER_FILE", "personality_owner.txt")
    if not personality_owner_file.is_file():
        raise ConfigError(f"Не найден файл характера для владельца: {personality_owner_file}")
    try:
        if not personality_owner_file.read_text(encoding="utf-8-sig").strip():
            raise ConfigError(f"Файл характера для владельца пустой: {personality_owner_file}")
    except OSError as exc:
        raise ConfigError(f"Не удалось прочитать {personality_owner_file}: {exc}") from exc

    log_level = _env_str("LOG_LEVEL", "INFO").upper()
''',
    "config: проверка файла владельца",
)

config = replace_once(
    config,
    "        personality_file=personality_file,\n",
    "        personality_file=personality_file,\n        personality_owner_file=personality_owner_file,\n",
    "config: возвращаемое значение",
)

# ---------- ai.py ----------
ai = replace_once(
    ai,
    "        self._personality = PersonalityLoader(settings.personality_file)\n",
    "        self._personality = PersonalityLoader(settings.personality_file)\n"
    "        self._owner_personality = PersonalityLoader(settings.personality_owner_file)\n",
    "ai: загрузчик характера владельца",
)

ai = replace_once(
    ai,
    "        history_lines: list[str],\n        author: str,\n        text: str,\n    ) -> str | None:\n",
    "        history_lines: list[str],\n        author: str,\n        text: str,\n"
    "        is_owner: bool = False,\n    ) -> str | None:\n",
    "ai: параметр is_owner",
)

ai = replace_once(
    ai,
    "        system_prompt = self._personality.get()\n",
    "        loader = self._owner_personality if is_owner else self._personality\n"
    "        system_prompt = loader.get()\n",
    "ai: выбор характера",
)

# ---------- bot.py ----------
bot = replace_once(
    bot,
    "        history = list(self.histories[job.chat_id])\n",
    "        history = [\n"
    "            f\"{entry.author}: {entry.text}\"\n"
    "            for entry in self.histories[job.chat_id]\n"
    "        ]\n",
    "bot: история строками",
)

bot = replace_once(
    bot,
    "                history_lines=history,\n                author=job.author,\n                text=job.text,\n",
    "                history_lines=history,\n                author=job.author,\n                text=job.text,\n"
    "                is_owner=job.is_owner,\n",
    "bot: передача is_owner в AI",
)

bot = replace_once(
    bot,
    "        await self._send(job, roast)\n",
    "        await self._send(job, roast)\n\n"
    "        self.histories[job.chat_id].append(\n"
    "            Entry(\n"
    "                author=\"Бот (ты)\",\n"
    "                text=roast,\n"
    "            )\n"
    "        )\n",
    "bot: ответы бота в историю",
)

bot = replace_once(
    bot,
    "        # 25% — медиа, которое раньше отправили участники группы\n",
    '''        # Владельцу отвечаем только текстом: медиа и голосовые не проходят через ИИ
        if job.is_owner:
            try:
                await bot.send_message(
                    chat_id=job.chat_id,
                    text=roast,
                    reply_to_message_id=job.message_id,
                )
            except TelegramError:
                logger.exception("Не удалось отправить ответ владельцу")
            return

        # 25% — медиа, которое раньше отправили участники группы
''',
    "bot: владельцу только текст",
)

bot = replace_once(
    bot,
    '    logger.info("Запускаю polling...")\n',
    '''    # httpx пишет в лог адреса запросов вместе с токеном и ключом
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logger.info("Запускаю polling...")
''',
    "bot: скрыть httpx из логов",
)

# ---------- запись ----------
for path in (config_path, ai_path, bot_path):
    shutil.copy(path, f"{path.name}.before_owner_mode")

config_path.write_text(config, encoding="utf-8")
ai_path.write_text(ai, encoding="utf-8")
bot_path.write_text(bot, encoding="utf-8")

owner_file = Path("personality_owner.txt")
if not owner_file.exists():
    owner_file.write_text(
        """Ты — бот в групповом чате Telegram. Сейчас ты отвечаешь ВЛАДЕЛЬЦУ бота — человеку, который тебя запустил.

Правила для этого собеседника:
- Никакого мата, грубых слов и оскорблений.
- Слово «roast» в запросе здесь означает добродушную, тёплую подколку или остроумную реплику. Можно слегка иронизировать, но по-дружески и с уважением.
- Длина: 1–2 коротких предложения, примерно до 200 символов.
- Опирайся на смысл его сообщения и на контекст чата.
- Не повторяй свои прошлые реплики (в контексте они помечены «Бот (ты)»).
- Пиши на языке чата (обычно русский).
- Выводи только текст реплики: без кавычек, пояснений и имени бота.
- Если человек пишет, что ему плохо, ответь коротко и по-доброму.
""",
        encoding="utf-8",
    )
    print("Создан personality_owner.txt")

print("ГОТОВО: режим владельца добавлен, история и логи исправлены.")