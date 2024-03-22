import json
from aiogram import Bot, Dispatcher

with open('data/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
TIMER = int(config["TIMER"])
GROUP_ID = config["GROUP_ID"]
ADMIN_ID = config["ADMIN_ID"]
bot = Bot(token=config["BOT_TOKEN"])
dp = Dispatcher(bot=bot)
