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
    winner = State()


# Start command handler
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    db.create_player(message.from_user.id, message.from_user.full_name)
    await message.reply(Localization.welcome)
    
# Play command handler
@dp.message_handler(Command("play"))
async def cmd_play(message: types.Message, state: FSMContext):
    session_id = db.create_session()
    db.create_game(message.from_user.id, session_id)
    await message.reply(Localization.number_players)
    await GameStates.num_players.set()

# Get number of players handler
@dp.message_handler(state=GameStates.num_players)
async def handle_num_players(message: types.Message, state: FSMContext):
    try:
        message.text.isdigit()
        num_players = int(message.text)
        if num_players >= 1:
            await state.update_data(num_players=num_players)
            data = await state.get_data()
            for i in range(num_players):
                player_name = f"player {i+1}"
                data[player_name] = []
                await state.update_data(data = data)
            await message.reply(Localization.number_rolls)
            await GameStates.num_rolls.set()
        else:
            await bot.send_message(chat_id=message.chat.id, text=Localization.number_players)    
    except:
        await bot.send_message(chat_id=message.chat.id, text=Localization.number_players)


# Get number of rolls handler
@dp.message_handler(state=GameStates.num_rolls)
async def handle_message(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num_rolls = int(message.text)
        await state.update_data(num_rolls = num_rolls)
        await message.reply(Localization.lets_play, reply_markup=GameState())
        await GameStates.rolls.set()
    else:
        await bot.send_message(chat_id=message.chat.id, text = Localization.number_rolls)



#Roll dice handler
@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=GameStates.rolls)
async def handle_button(callback_query: types.CallbackQuery, state: FSMContext):
    dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
    dice_roll_value = dice_roll["dice"]["value"]
    data = await state.get_data()
    print(data)
    num_rolls = data["num_rolls"]
    num_gamers = data["num_players"]
    print((num_rolls))
    print((num_gamers))
    for i in range(num_gamers):
        print(i)
        await state.update_data(i = [])
        num_player = i
        rolls = data[num_player]
        rolls.append(dice_roll_value)
        result = f"Roll of player {num_player}: {dice_roll_value}\n"
    if len(rolls) == num_rolls:
        await asyncio.sleep(3)
        total_results = []
        for i in range(data["num_players"]):
            player_result = []
            for j in range(num_rolls):
                player_result.append(rolls[i*num_rolls+j])
            total_results.append(sum(player_result))
            result += f"Player {i+1}: {player_result}\n"
        winner_index = total_results.index(max(total_results))
        result += f"Winner: Player {winner_index+1}\nTotal result: {total_results}"
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
        await state.finish()
    else:
        await asyncio.sleep(3)
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState()) 
        await state.update_data(rolls=rolls)


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