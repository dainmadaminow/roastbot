from pathlib import Path

p = Path("media_memory.py")

code = '''import json
import random
from pathlib import Path


class MediaMemory:
    def __init__(self, path="data/media_memory.json", max_items=200):
        self.path = Path(path)
        self.max_items = max_items
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            try:
                self.data = json.loads(
                    self.path.read_text(encoding="utf-8")
                )
            except Exception:
                self.data = {}
        else:
            self.data = {}

        for key in ("photos", "gifs", "stickers", "voices"):
            self.data.setdefault(key, [])

    def save(self):
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, kind, file_id):
        if kind not in self.data or not file_id:
            return

        if file_id not in self.data[kind]:
            self.data[kind].append(file_id)

        self.data[kind] = self.data[kind][-self.max_items:]
        self.save()

    def random(self, kind):
        items = self.data.get(kind, [])
        return random.choice(items) if items else None

    def count(self, kind):
        return len(self.data.get(kind, []))
'''

p.write_text(code, encoding="utf-8")
print("ГОТОВО: MediaMemory восстановлен")