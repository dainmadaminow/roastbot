"""Настройки бота. Все значения читаются из файла .env (или из переменных окружения)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


class ConfigError(Exception):
    """Ошибка в настройках (с понятным сообщением для человека)."""


def _env_str(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _env_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = _env_str(name)
    if not raw:
        value = default
    else:
        try:
            value = int(raw)
        except ValueError:
            raise ConfigError(f"{name} должен быть целым числом, а сейчас там: {raw!r}") from None
    if not (min_value <= value <= max_value):
        raise ConfigError(f"{name} должен быть от {min_value} до {max_value}, а сейчас: {value}")
    return value


def _env_float(name: str, default: float, min_value: float, max_value: float) -> float:
    raw = _env_str(name)
    if not raw:
        value = default
    else:
        try:
            value = float(raw.replace(",", "."))
        except ValueError:
            raise ConfigError(f"{name} должен быть числом, а сейчас там: {raw!r}") from None
    if not (min_value <= value <= max_value):
        raise ConfigError(f"{name} должен быть от {min_value} до {max_value}, а сейчас: {value}")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = _env_str(name).lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes", "on", "да"):
        return True
    if raw in ("0", "false", "no", "off", "нет"):
        return False
    raise ConfigError(f"{name} должен быть true или false, а сейчас там: {raw!r}")


def _env_path(name: str, default: str) -> Path:
    path = Path(_env_str(name, default))
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def _check_text_file(path: Path, title: str) -> None:
    if not path.is_file():
        raise ConfigError(f"Не найден файл {title}: {path}")
    try:
        if not path.read_text(encoding="utf-8-sig").strip():
            raise ConfigError(f"Файл {title} пустой: {path}")
    except OSError as exc:
        raise ConfigError(f"Не удалось прочитать {path}: {exc}") from exc


@dataclass(frozen=True)
class Settings:
    # Telegram
    telegram_token: str
    admin_only_toggle: bool

    # AI API
    ai_api_key: str
    ai_base_url: str
    ai_model: str
    ai_temperature: float
    ai_max_tokens: int
    ai_timeout_seconds: float
    ai_max_retries: int
    max_reply_chars: int

    # Контекст
    max_context_messages: int
    max_message_chars: int

    # Очередь и задержки
    min_delay_seconds: float
    max_delay_seconds: float
    max_concurrent_requests: int
    chat_queue_size: int
    max_job_age_seconds: int

    # Файлы
    personality_file: Path
    personality_owner_file: Path
    state_file: Path

    # Логи
    log_level: str


def load_settings() -> Settings:
    # utf-8-sig, чтобы .env, сохранённый Блокнотом с BOM, читался нормально
    load_dotenv(BASE_DIR / ".env", encoding="utf-8-sig")

    telegram_token = _env_str("TELEGRAM_BOT_TOKEN")
    if not telegram_token or ":" not in telegram_token:
        raise ConfigError(
            "Не задан TELEGRAM_BOT_TOKEN. Получите токен у @BotFather и вставьте его в .env "
            "или в переменные окружения (он выглядит примерно так: 123456789:AAH...)."
        )

    ai_api_key = _env_str("AI_API_KEY")
    if not ai_api_key:
        raise ConfigError("Не задан AI_API_KEY. Вставьте ключ AI API в .env или в переменные окружения.")

    min_delay = _env_float("MIN_DELAY_SECONDS", 1.0, 0.0, 60.0)
    max_delay = _env_float("MAX_DELAY_SECONDS", 3.0, 0.0, 60.0)
    if min_delay > max_delay:
        raise ConfigError("MIN_DELAY_SECONDS не может быть больше MAX_DELAY_SECONDS.")

    personality_file = _env_path("PERSONALITY_FILE", "personality.txt")
    _check_text_file(personality_file, "характера бота")

    personality_owner_file = _env_path("PERSONALITY_OWNER_FILE", "personality_owner.txt")
    _check_text_file(personality_owner_file, "характера для владельца")

    log_level = _env_str("LOG_LEVEL", "INFO").upper()
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise ConfigError("LOG_LEVEL должен быть одним из: DEBUG, INFO, WARNING, ERROR.")

    return Settings(
        telegram_token=telegram_token,
        admin_only_toggle=_env_bool("ADMIN_ONLY_TOGGLE", False),
        ai_api_key=ai_api_key,
        ai_base_url=_env_str("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        ai_model=_env_str("AI_MODEL", "gemini-2.5-flash-lite"),
        ai_temperature=_env_float("AI_TEMPERATURE", 1.0, 0.0, 2.0),
        ai_max_tokens=_env_int("AI_MAX_TOKENS", 1000, 20, 4000),
        ai_timeout_seconds=_env_float("AI_TIMEOUT_SECONDS", 30.0, 3.0, 300.0),
        ai_max_retries=_env_int("AI_MAX_RETRIES", 2, 0, 10),
        max_reply_chars=_env_int("MAX_REPLY_CHARS", 300, 50, 4000),
        max_context_messages=_env_int("MAX_CONTEXT_MESSSAGES", 20, 1, 100),
        max_message_chars=_env_int("MAX_MESSAGE_CHARS", 500, 50, 4000),
        min_delay_seconds=min_delay,
        max_delay_seconds=max_delay,
        max_concurrent_requests=_env_int("MAX_CONCURRENT_REQUESTS", 3, 1, 20),
        chat_queue_size=_env_int("CHAT_QUEUE_SIZE", 20, 1, 500),
        max_job_age_seconds=_env_int("MAX_JOB_AGE_SECONDS", 90, 5, 3600),
        personality_file=personality_file,
        personality_owner_file=personality_owner_file,
        state_file=_env_path("STATE_FILE", "data/state.json"),
        log_level=log_level,
    )