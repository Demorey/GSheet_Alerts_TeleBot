from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bot, GROUP_ID


async def send_notification(text, url):
    reply_markup = InlineKeyboardMarkup(row_width=1)
    reply_markup.add(InlineKeyboardButton(f'Перейти к таблице', url=url))
    await bot.send_message(GROUP_ID, text, parse_mode="HTML", reply_markup=reply_markup)
