"""Хранение состояния /on и /off для каждой группы (в JSON-файле)."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ChatStateStore:
    """Помнит, включён ли бот в каждой группе. Если группа неизвестна — бот включён."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, bool] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            chats = raw.get("chats", {})
            self._data = {str(key): bool(value) for key, value in chats.items()}
        except (OSError, ValueError, AttributeError):
            logger.exception("Не удалось прочитать %s, начинаю с чистого состояния", self._path)
            self._data = {}

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._path.with_suffix(".tmp")
            tmp_path.write_text(
                json.dumps({"chats": self._data}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp_path, self._path)
        except OSError:
            logger.exception("Не удалось сохранить состояние в %s", self._path)

    def is_enabled(self, chat_id: int) -> bool:
        return self._data.get(str(chat_id), True)

    def set_enabled(self, chat_id: int, enabled: bool) -> None:
        self._data[str(chat_id)] = enabled
        self._save()
        