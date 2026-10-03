from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

old = '''    async def _send(self, job: Job, roast: str) -> None:
        bot = self.application.bot

        # Примерно 30% ответов — GIF, если GIPHY настроен
'''

new = '''    async def _send(self, job: Job, roast: str) -> None:
        bot = self.application.bot

        # 25% — медиа, которое раньше отправили участники группы
        if random.random() < 0.25:
            if await self._send_saved_media(job, roast):
                return

        # Примерно 30% ответов — GIF, если GIPHY настроен
'''

if old not in s:
    raise SystemExit("Нужный участок _send не найден")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

print("ГОТОВО: сохранённые медиа подключены к рандомным ответам")