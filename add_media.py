from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

old = "from state import ChatStateStore"
new = old + "\nfrom media_memory import MediaMemory"

if "from media_memory import MediaMemory" not in s:
    if old not in s:
        raise SystemExit("Строка импорта не найдена")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: MediaMemory подключён")