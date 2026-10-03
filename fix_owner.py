import shutil
from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

shutil.copy(p, "bot.py.bak")


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Не нашёл ровно одно совпадение для: {name}. Ничего не изменено.")
    return text.replace(old, new, 1)


s = replace_once(
    s,
    '''        # Владелец полностью игнорируется
        if self.is_owner(user_id):
            logger.info(
                "Сообщение владельца пропущено. ID: %s",
                user_id,
            )
            return

''',
    "",
    "блок пропуска владельца",
)

s = replace_once(
    s,
    "    text: str\n    user_id: int\n",
    "    text: str\n    user_id: int\n    is_owner: bool = False\n",
    "поле is_owner в Job",
)

s = replace_once(
    s,
    "            user_id=user_id or 0,\n",
    "            user_id=user_id or 0,\n            is_owner=self.is_owner(user_id),\n",
    "создание Job",
)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: владелец больше не игнорируется, копия сохранена в bot.py.bak")