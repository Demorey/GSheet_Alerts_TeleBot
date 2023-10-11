import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bot


async def send_notification(group_id, text, url):
    reply_markup = InlineKeyboardMarkup(row_width=1)
    reply_markup.add(InlineKeyboardButton(f'Перейти к таблице', url=url))
    if text.startswith("Ошибка"):
        with open('data/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        group_id = config["ADMIN_ID"]
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            await bot.send_message(group_id, text[x:x + 4096], parse_mode="HTML", reply_markup=reply_markup)
    else:
        await bot.send_message(group_id, text, parse_mode="HTML", reply_markup=reply_markup)
