from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import bot, ADMIN_ID


async def send_notification(group_id: str, data: dict, url: str):
    mailing_list = [group_id]
    reply_markup = InlineKeyboardBuilder()
    reply_markup.row(InlineKeyboardButton(text="Перейти к таблице", url=url))
    if data["error"]:
        await bot.send_message(ADMIN_ID, data["error"], parse_mode="HTML", reply_markup=reply_markup.as_markup())
    if data["changes"]:
        text = data["changes"]
        if group_id != ADMIN_ID:
            mailing_list.append(ADMIN_ID)
        if len(text) > 4096:
            for x in range(0, len(text), 4096):
                for group_id in mailing_list:
                    await bot.send_message(group_id, text[x:x + 4096], parse_mode="HTML",
                                           reply_markup=reply_markup.as_markup())
        else:
            for group_id in mailing_list:
                await bot.send_message(group_id, text, parse_mode="HTML", reply_markup=reply_markup.as_markup())
