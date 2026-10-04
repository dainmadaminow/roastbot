from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from google import genai

logger = logging.getLogger(__name__)


class VoiceTranscriber:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("AI_API_KEY не задан")

        self.client = genai.Client(api_key=api_key)

    async def transcribe(self, audio_path: Path) -> str:
        try:
            # Для распознавания речи используем специальную модель
            # Gemini 3.5 Transcribe через актуальный Interactions API.
            audio_file = await asyncio.to_thread(
                self.client.files.upload,
                file=str(audio_path),
            )

            interaction = await asyncio.to_thread(
                self.client.interactions.create,
                model="gemini-3.5-transcribe",
                input=[
                    {
                        "type": "audio",
                        "uri": audio_file.uri,
                        "mime_type": audio_file.mime_type or "audio/ogg",
                    }
                ],
            )

            text = (getattr(interaction, "output_text", "") or "").strip()

            if text:
                logger.info(
                    "Голосовое распознано: %s",
                    text[:500],
                )
            else:
                logger.warning("Gemini не вернул текст голосового")

            return text

        except Exception:
            logger.exception("Ошибка распознавания голосового")
            return ""

    async def close(self) -> None:
        # У текущего SDK отдельное закрытие клиента не требуется.
        return
