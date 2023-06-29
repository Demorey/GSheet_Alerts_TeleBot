import asyncio
from aiogram.utils import executor
from create_bot import dp, bot


async def on_startup(_):
    bot_name = await bot.get_me()
    print('Запущен бот: '+bot_name.first_name)


if __name__ == '__main__':
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.create_task(handlers.client.task())

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)