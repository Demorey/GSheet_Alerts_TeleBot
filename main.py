import os
import logging
from logging.handlers import RotatingFileHandler

from aiogram.utils import executor
from create_bot import dp, bot
import handlers.message_handler

if not os.path.exists("logs/debug_loger.log"):
    os.makedirs("logs/")
    logs = open("logs/debug_loger.log", "w")
    logs.close()
logging.basicConfig(level=logging.DEBUG, encoding='utf-8',
                    handlers=[RotatingFileHandler('logs/debug_loger.log', maxBytes=5000000, backupCount=1)],
                    format="%(asctime)s - [%(levelname)s] - %(funcName)s: %(lineno)d - %(message)s")


async def on_startup(_):
    bot_name = await bot.get_me()
    print('Запущен бот: '+bot_name.first_name)


if __name__ == '__main__':
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.create_task(handlers.client.task())

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)