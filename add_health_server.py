import shutil
from pathlib import Path


def replace_once(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"[{name}] не нашёл ровно одно совпадение. Ничего не изменено.")
    return text.replace(old, new, 1)


p = Path("bot.py")
s = p.read_text(encoding="utf-8")

if "start_health_server" in s:
    raise SystemExit("Патч уже применён.")

s = replace_once(
    s,
    'async def post_init(\n    application: Application,\n) -> None:\n    settings = application.bot_data["settings"]\n',
    '''async def _health_handler(reader, writer) -> None:
    try:
        await asyncio.wait_for(reader.read(1024), timeout=5)
    except Exception:
        pass

    try:
        writer.write(
            b"HTTP/1.1 200 OK\\r\\n"
            b"Content-Type: text/plain\\r\\n"
            b"Content-Length: 2\\r\\n"
            b"Connection: close\\r\\n\\r\\n"
            b"ok"
        )
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()


async def start_health_server():
    """На Render слушаем порт PORT, чтобы бесплатный Web Service считался живым."""
    port = os.getenv("PORT", "").strip()

    if not port:
        return None

    server = await asyncio.start_server(_health_handler, "0.0.0.0", int(port))
    logger.info("Health-сервер запущен на порту %s", port)
    return server


async def post_init(
    application: Application,
) -> None:
    settings = application.bot_data["settings"]

    application.bot_data["health_server"] = await start_health_server()
''',
    "post_init",
)

s = replace_once(
    s,
    '    ai = application.bot_data.get("ai")\n    giphy = application.bot_data.get("giphy")\n',
    '''    health_server = application.bot_data.get("health_server")

    if health_server is not None:
        health_server.close()

    ai = application.bot_data.get("ai")
    giphy = application.bot_data.get("giphy")
''',
    "post_shutdown",
)

shutil.copy(p, "bot.py.before_health")
p.write_text(s, encoding="utf-8")
print("ГОТОВО: health-сервер добавлен")