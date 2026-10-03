from pathlib import Path

p = Path("bot.py")
s = p.read_text(encoding="utf-8")

marker = '''    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            on_my_chat_member,
        )
    )
'''

new_handler = '''    application.add_handler(
        MessageHandler(
            (
                filters.PHOTO
                | filters.ANIMATION
                | filters.Sticker.ALL
                | filters.VOICE
            )
            & filters.ChatType.GROUPS
            & filters.UpdateType.MESSAGE,
            on_media,
        )
    )

'''

if "on_media," not in s:
    if marker not in s:
        raise SystemExit("Нужный блок обработчика не найден")
    s = s.replace(marker, new_handler + marker, 1)

p.write_text(s, encoding="utf-8")
print("ГОТОВО: on_media подключён")