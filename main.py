from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import logging
from gameplay.dice import DiceGame
from resources.Localization import Localization
from aiogram.dispatcher.filters.state import State, StatesGroup


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


# Start command handler
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    db.create_player(message.from_user.id, message.from_user.full_name)
    await message.reply(Localization.welcome)
    

@dp.message_handler(Command("play"))
async def cmd_play(message: types.Message, state: FSMContext):
    session_id = db.create_session()
    db.create_game(message.from_user.id, session_id)
    await message.reply(Localization.number_rolls)
    
# class Rolls_Dice(StatesGroup):
#     first_roll = State()
#     second_roll = State()
#     third_roll = State()

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num_rolls = int(message.text)
        await state.update_data(num_rolls = num_rolls)
        await state.update_data(rolls = [])
        data = await state.get_data()
        print(data)
        print(type(data["rolls"]))
        
        await message.reply(Localization.lets_play, reply_markup=GameState())
    else:
        await bot.send_message(chat_id=message.chat.id, text = Localization.number_rolls)



@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE)
async def handle_button(callback_query: types.CallbackQuery, state: FSMContext):
    dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
    dice_roll_value = dice_roll["dice"]["value"]
    data = await state.get_data()
    print(data)
    num_rolls = data["num_rolls"]
    print(num_rolls)
    rolls = data["rolls"]
    rolls.append(dice_roll_value)
    result = f"Roll {len(rolls)}: {dice_roll_value}\n"
    if len(rolls) == num_rolls:
        result += "Total result: " + str(sum(rolls))
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
        await state.finish()
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState()) 
        await state.update_data(rolls=rolls)
        print(data)



# Callback query handler
# @dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE)
# async def roll_dice_callback(callback_query: types.CallbackQuery, state: FSMContext):
#     # first roll the dice
#     dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id, reply_markup=GameState())
#     dice_value = dice_roll["dice"]["value"]
#     await state.update_data(first = dice_value)
#     await state.set_state(Rolls_Dice.first_roll)


# @dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=Rolls_Dice.first_roll)
# async def roll_dice_callback(callback_query: types.CallbackQuery, state: FSMContext):
#     dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id, reply_markup=GameState())
#     dice_value = dice_roll["dice"]["value"]
#     await state.update_data(second = dice_value)
#     await state.set_state(Rolls_Dice.second_roll)

# @dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=Rolls_Dice.second_roll)
# async def roll_dice_callback(callback_query: types.CallbackQuery, state: FSMContext):
#     dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
#     dice_value = dice_roll["dice"]["value"]
#     await state.update_data(third = dice_value)
#     data_rolls = await state.get_data()
#     rolls = sum(data_rolls[x] for x in data_rolls)
#     text = f"The total result of the dice rolls is {rolls}"
#     await bot.send_message(chat_id=callback_query.message.chat.id, text=text)
#     await state.set_state(Rolls_Dice.third_roll)
    




    # # Update the message with the dice result
    # await bot.edit_message_text(Localization.rolled.format(dice_value),
    #                             callback_query.message.chat.id,
    #                             callback_query.message.message_id)

    # Save the game result to the database
    # db.insert_game_result(user_id, user_name, dice_value)

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