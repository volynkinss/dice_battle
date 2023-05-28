from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from db.game_db import SQLiteDB
from bot_setup import bot
import logging
from handlers.handlers import setup_handlers

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLiteDB("game.db")
db.connect()
db.init_game_table()

setup_handlers(dp)

if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        bot.close()
        db.disconnect()
