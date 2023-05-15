from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import random
import logging
from db.game_db import SQLiteDB
from token_for_bot import bot_token

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLiteDB("game.db")
db.init_game_table()


# Game states
class GameState(types.InlineKeyboardMarkup):
    ROLL_DICE = 'roll_dice'

    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton('Roll Dice', callback_data=self.ROLL_DICE))

# Start command handler
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Welcome to the dice game! Use the /play command to start the game.")

    

@dp.message_handler(Command("play"))
async def cmd_play(message: types.Message):
    await message.reply("Let's play the dice game! Click the 'Roll Dice' button to roll the dice.",
                        reply_markup=GameState())

# Callback query handler
@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE)
async def roll_dice_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    # Get the user who initiated the game
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.username or callback_query.from_user.first_name

    # Roll the dice
    dice_value = random.randint(1, 6)


    # Update the message with the dice result
    await bot.edit_message_text(f"You rolled {dice_value}!",
                                callback_query.message.chat.id,
                                callback_query.message.message_id)

    # Save the game result to the database
    db.insert_data("games", (user_id, user_name, dice_value))

    # Reset the game state
    await state.reset_state()

    # TODO: Implement game logic (e.g., track scores, determine the winner, etc.)
    

# Run the bot
if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        # Close the bot and database connection
        bot.close()
        db.disconnect()
