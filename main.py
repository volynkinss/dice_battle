from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import logging
from gameplay.dice import DiceGame
from resources.Localization import Localization
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio



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
    num_players = State()
    num_rolls = State()
    rolls = State()
    play = State()
    winner = State()


players = []
num_players = 2
num_rolls = 3
rolls = {}
total = {}

# Start command handler
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(rolls = rolls,
                            num_players = num_players,
                            num_rolls = num_rolls)
    data = await state.get_data()
    print(data)
    if user_id not in players:
        players.append(user_id)
        total.update({user_id : []})
        rolls.update({user_id : []})
        await state.update_data(players = players,
                                rolls = rolls,
                                total = total)

    if len(players) == num_players:
        await GameStates.play.set()
        await message.reply(Localization.welcome)
    else:
        text = "Search for the enemy"
        await message.reply(text = text)
    data = await state.get_data()
    print(data)


# Play command handler
@dp.message_handler(Command("play"), state=GameStates.play)
async def cmd_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    num_rolls = data["num_rolls"]
    num_players = data["num_players"]
    players = data["players"]
    while len(players) != num_players:
        await message.reply(Localization.waiting)
        await asyncio.sleep(20)
    await message.reply(Localization.lets_play.format(num_rolls), reply_markup=GameState())
    await GameStates.rolls.set()





#Roll dice handler
@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=GameStates.rolls)
async def handle_button(callback_query: types.CallbackQuery, state: FSMContext):
    dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
    dice_roll_value = dice_roll["dice"]["value"]
    player_name = dice_roll["chat"]["first_name"]
    data = await state.get_data()
    num_rolls = data["num_rolls"]
    user_id = callback_query.from_user.id
    rolls = data["rolls"]
    rolls[user_id].append(dice_roll_value)
    print(rolls)
    print(data)
    await state.update_data({"rolls": rolls})
    data = await state.get_data()
    print(data)
    # await asyncio.sleep(3)
    result = f"Roll №{len(rolls)} by {player_name}: {dice_roll_value}\n"
    if len(rolls[user_id]) == num_rolls:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
        # await asyncio.sleep(3)
        data = await state.get_data()
        total = data["total"]
        print(total)
        total_result = sum(rolls)
        result = f"Total of {num_rolls} rolls by {player_name} is {total_result}"
        total[user_id].append(total_result)
        await state.update_data({"total":total})
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result) 
        data = await state.get_data()
        total = data["total"]
        print(data)
        print(total)
        # users_id = list(total.keys())
        # user1 = users_id[0]
        # total_u_1 = int(total[user1][0])
        # user2 = users_id[1]
        # total_u_2 = int(total[user2][0])
        # if total_u_1 == total_u_2:
        #     text = "ничья"
        # elif total_u_1 > total_u_2:
        #     text = f"Player {user1} win"
        # else:
        #     text = f"Player {user2} win"
        # await bot.send_message(chat_id=callback_query.message.chat.id, text=text)

    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState())

    

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