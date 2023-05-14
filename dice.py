from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot_token = 'YOUR_BOT_TOKEN'
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize SQLite database connection
conn = sqlite3.connect('game.db')
cursor = conn.cursor()

# Create a table to store game results
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        player_name TEXT,
        dice_value INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

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

# Play command handler
@dp.message_handler(Command("play"))
async def cmd_play(message: types.Message):
    await message.reply("Let's play the dice game! Click the 'Roll Dice' button to roll the dice.",
                        reply_markup=GameState())

# Callback query handler
@dp.callback_query_handler(func=lambda c: c.data == GameState.ROLL_DICE)
async def roll_dice_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    # Get the user who initiated the game
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.username or callback_query.from_user.first_name

    # Roll the dice
    dice_value = random.randint(1, 6)

    # Update the message with the dice result
    await bot.edit_message_text(f"You rolled a {dice_value}!",
                                callback_query.message.chat.id,
                                callback_query.message.message_id)

    # Save the game result to the database
    cursor.execute('''
        INSERT INTO games (player_id, player_name, dice_value) VALUES (?, ?, ?)
    ''', (user_id, user_name, dice_value))
    conn.commit()

    # Reset the game state
    await state.reset_state()

    # TODO: Implement game logic (e.g., track scores, determine the winner, etc.)

# Run the bot
if __name__ == '__main__':
    try:
        dp.run_polling()
    finally:
        # Close the bot and database connection
        bot.close()
        conn.close()