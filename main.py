import asyncio
import json
import os
import logging
from logging.handlers import RotatingFileHandler

import gspread

import notification_sender
from create_bot import dp, bot, TIMER, GROUP_ID, ADMIN_ID
from handlers.gsheets_handler import spreadsheet_check

if not os.path.exists("logs/"):
    os.makedirs("logs/")
    logs = open("logs/debug_loger.log", "w")
    logs.close()
logging.basicConfig(level=logging.DEBUG, encoding='utf-8',
                    handlers=[RotatingFileHandler('logs/debug_loger.log', maxBytes=5000000, backupCount=1)],
                    format="%(asctime)s - [%(levelname)s] - %(funcName)s: %(lineno)d - %(message)s")


async def task():
    await asyncio.sleep(5)
    while True:
        try:
            gc = gspread.service_account(filename='data/service_acc.json')

            with open('data/spreadsheets_data.json', 'r', encoding='utf-8') as f:
                spreadsheet_data = json.load(f)
            spreadsheet_list = spreadsheet_data["SPREADSHEETS"]
            for i, spreadsheet in enumerate(spreadsheet_list):
                result = await spreadsheet_check(gc, i, spreadsheet, spreadsheet_data)
                if not result:
                    continue
                if result.startswith("Ошибка"):
                    await notification_sender.send_notification(ADMIN_ID, result, spreadsheet["url"])
                else:
                    group_id = spreadsheet.get('group_id')
                    if not group_id:
                        group_id = GROUP_ID
                    await notification_sender.send_notification(group_id, result, spreadsheet["url"])
            await asyncio.sleep(TIMER)
        except TimeoutError:
            await asyncio.sleep(600)


async def bot_start():
    try:
        bot_name = await bot.get_me()
        print('Запущен бот: ' + bot_name.first_name)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main():
    tasks = [task(), bot_start()]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
