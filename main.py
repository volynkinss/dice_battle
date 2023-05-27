from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import logging
from resources.Localization import Localization
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



from db.game_db import SQLiteDB
from gameplay.game_state import GameState
from token_for_bot import bot_token

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLiteDB("game.db")
db.connect()
db.init_game_table()

class GameStates(StatesGroup):
    play = State()
    rolls = State()
    winner = State()


num_players = 2
num_rolls = 3
players = []
rolls = {}
total = {}
name = {}

# Start command handler
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if len(players) >= num_players:
        text = "Sorry, all playing places are taken. Try again later"
        await message.reply(text)
    else:
        if user_id not in players:
            players.append(user_id)
            rolls.update({user_id : []})
            total.update({user_id : []})
            name.update({user_id : user_name})
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Start Game', callback_data='play'))
        await message.reply(Localization.lets_play.format(num_rolls), reply_markup=markup)
        await GameStates.play.set()


# Play command handler
@dp.callback_query_handler(lambda c: c.data == 'play', state=GameStates.play)
async def play_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    if len(players) != num_players:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.waiting)
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.lets_play.format(num_rolls), reply_markup=GameState())
        await GameStates.rolls.set()




#Roll dice handler
@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=GameStates.rolls)
async def roll_dice_button(callback_query: types.CallbackQuery, state: FSMContext):
    dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
    dice_roll_value = dice_roll["dice"]["value"]
    user_id = callback_query.from_user.id
    rolls[user_id].append(dice_roll_value)
    result = f"Roll №{len(rolls[user_id])} by {name[user_id]}: {dice_roll_value}\n"
    if len(rolls[user_id]) == num_rolls:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
        total_result = sum(rolls[user_id])
        result = f"Total of {num_rolls} rolls by {name[user_id]} is {total_result}"
        total.update({user_id:total_result})
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Show winner', callback_data='winner'))
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=markup)
        await GameStates.winner.set()
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState())

@dp.callback_query_handler(lambda c: c.data == 'winner', state=GameStates.winner)
async def winner_button(callback_query: types.CallbackQuery, state: FSMContext):
    if all(total.values()):
        list_total_values = list(total.values())
        if list_total_values[0] == list_total_values[1]:
            winner = f" After all rolls players have the same result : {list_total_values[0]}. Good game!🤝 \nIf you want to play again, click /start"
        else:
            max_player_id = max(total, key=total.get)
            max_player_name = name[max_player_id]
            max_player_score = total[max_player_id]
            winner = f" After all rolls of players winner is {max_player_name} with total {max_player_score}. Congratulations! \nIf you want to play again, click /start"
        await bot.send_message(chat_id=callback_query.message.chat.id, text=winner)
        await state.reset_state()
        players.clear()
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Show winner', callback_data='winner'))
        text = "Waiting for the opponent to finish his throws"
        await bot.send_message(chat_id=callback_query.message.chat.id, text=text, reply_markup=markup)
    

    # TODO: Implement game logic (e.g., track scores, determine the winner, etc.)
    

# Run the bot
if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        # Close the bot and database connection
        bot.close()
        db.disconnect()


### game step by step:
#player 1 starting new game
#session is added in state "started"
#player 2 starting new game
#check if any started sessions available
#create game, reference players and session
#session state changed to "ongoing"
#player 1 asked to do a turn /dice //save
#player 2 asked to do a turn /dice //save
#save turn result 
#player 1 asked to do a turn /dice //save
#player 2 asked to do a turn /dice //save
#save turn result
#player 1 asked to do a turn /dice //save
#player 2 asked to do a turn /dice //save
#save turn result
#determine winner by sum of 3 dice of each player
#save total dice result for each player
#session to state "finished"
#game winner and score update