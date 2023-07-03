import json
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

with open('data/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
TIMER = int(config["TIMER"])
GROUP_ID = config["GROUP_ID"]
bot = Bot(token=config["BOT_TOKEN"])
dp = Dispatcher(bot, storage=MemoryStorage())

