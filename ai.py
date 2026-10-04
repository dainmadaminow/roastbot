"""Работа с Gemini AI API через OpenAI-совместимый интерфейс."""
from __future__ import annotations

import logging
from pathlib import Path

import httpx

from config import Settings

logger = logging.getLogger(__name__)

_QUOTE_PAIRS = {('"', '"'), ("'", "'"), ("«", "»"), ("“", "”"), ("„", "“")}
_PREFIXES = ("бот (ты):", "бот:", "bot:", "ответ:", "roast:")


class PersonalityLoader:
    """Читает характер бота из файла и подхватывает изменения без перезапуска."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._mtime: float | None = None
        self._text = ""

    def get(self) -> str:
        try:
            mtime = self._path.stat().st_mtime
            if mtime != self._mtime:
                text = self._path.read_text(encoding="utf-8-sig").strip()
                if text:
                    self._text = text
                    self._mtime = mtime
                    logger.info("Характер бота загружен из %s", self._path.name)
                else:
                    logger.warning("Файл %s пустой", self._path.name)
        except OSError:
            logger.exception("Не удалось прочитать %s", self._path)

        return self._text


def build_user_prompt(history_lines: list[str], author: str, text: str) -> str:
    """Создаёт запрос для ИИ."""
    transcript = "\n".join(history_lines) if history_lines else "(пока пусто)"

    return (
        "Последние сообщения чата (от старых к новым):\n"
        f"{transcript}\n\n"
        f"НОВОЕ сообщение от {author}:\n{text}\n\n"
        "Придумай один НОВЫЙ короткий ответ именно на это сообщение, "
        "учитывая контекст и свою роль. Не повторяй прежние ответы бота. "
        "Выведи только текст реплики."
    )


def clean_reply(raw: str | None, max_chars: int) -> str | None:
    """Очищает ответ от лишних символов."""
    if not raw:
        return None

    text = raw.strip()

    if len(text) >= 2 and (text[0], text[-1]) in _QUOTE_PAIRS:
        text = text[1:-1].strip()

    lowered = text.lower()

    for prefix in _PREFIXES:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    if not text:
        return None

    if len(text) > max_chars:
        cut = text[:max_chars]
        last_end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))

        if last_end >= max_chars // 2:
            text = cut[:last_end + 1]
        else:
            text = cut.rstrip() + "…"

    return text


class AIClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._personality = PersonalityLoader(settings.personality_file)
        self._owner_personality = PersonalityLoader(settings.personality_owner_file)

        self._client = httpx.AsyncClient(
            timeout=settings.ai_timeout_seconds
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def generate_roast(
        self,
        history_lines: list[str],
        author: str,
        text: str,
        is_owner: bool = False,
    ) -> str | None:
        """Возвращает ответ или None при ошибке."""

        loader = self._owner_personality if is_owner else self._personality
        system_prompt = loader.get()
        user_prompt = build_user_prompt(history_lines, author, text)

        try:
            raw = await self._complete(system_prompt, user_prompt)
        except Exception as exc:
            logger.error(
                "Ошибка AI API: %s: %s",
                type(exc).__name__,
                exc,
            )
            return None

        reply = clean_reply(
            raw,
            self._settings.max_reply_chars,
        )

        if reply is None:
            logger.warning("AI вернул пустой ответ")

        return reply

    async def _complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Отправляет запрос в AI API."""
        base_url = self._settings.ai_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self._settings.ai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self._settings.ai_temperature,
            "max_tokens": self._settings.ai_max_tokens,
        }

        response = await self._client.post(
            url,
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            logger.error(
                "AI API HTTP %s: %s",
                response.status_code,
                response.text[:1000],
            )
            response.raise_for_status()

        data = response.json()
        logger.debug("AI RESPONSE: %s", data)
        
        choices = data.get("choices", [])

        if not choices:
            logger.warning("AI не вернул choices: %s", data)
            return ""

        return choices[0].get("message", {}).get("content", "")