from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

old = "self.giphy = giphy"
new = old + "\n        self.media_memory = MediaMemory()"

if "self.media_memory = MediaMemory()" not in s:
    if old not in s:
        raise SystemExit("Нужная строка не найдена")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: память медиа подключена к RoastService")