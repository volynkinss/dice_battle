from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import logging
from resources.localization import Localization
from resources.commands import Commands
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.game_db import SQLiteDB
from gameplay.game_state import GameState
from token_for_bot import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLiteDB("game.db")
db.connect()
db.init_game_table()


class GameStates(StatesGroup):
    play = State()
    rolls = State()
    winner = State()


NUM_PLAYERS = 2
NUM_ROLLS = 3
players = []
rolls = {}
total = {}
name = {}


@dp.message_handler(Command(Commands.start))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if len(players) >= NUM_PLAYERS:
        text = Localization.sorry
        await message.reply(text)
    else:
        if user_id not in players:
            players.append(user_id)
            rolls.update({user_id: []})
            total.update({user_id: []})
            name.update({user_id: user_name})
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(Localization.start_game, callback_data=Commands.play))
        await message.reply(Localization.lets_play.format(NUM_ROLLS), reply_markup=markup)
        await GameStates.play.set()


@dp.callback_query_handler(lambda c: c.data == Commands.play, state=GameStates.play)
async def play_button(callback_query: types.CallbackQuery, state: FSMContext):
    if len(players) != NUM_PLAYERS:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.waiting)
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.lets_play.format(NUM_ROLLS), reply_markup=GameState())
        await GameStates.rolls.set()


@dp.callback_query_handler(lambda c: c.data == GameState.ROLL_DICE, state=GameStates.rolls)
async def roll_dice_button(callback_query: types.CallbackQuery, state: FSMContext):
    dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
    dice_roll_value = dice_roll["dice"]["value"]
    user_id = callback_query.from_user.id
    rolls[user_id].append(dice_roll_value)
    result = Localization.dice_result.format(len(rolls[user_id]), name[user_id], dice_roll_value)
    if len(rolls[user_id]) == NUM_ROLLS:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
        total_result = sum(rolls[user_id])
        result = Localization.total_result.format(NUM_ROLLS, name[user_id], total_result)
        total.update({user_id: total_result})
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(Localization.show_winner, callback_data=Commands.winner))
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=markup)
        await GameStates.winner.set()
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState())


@dp.callback_query_handler(lambda c: c.data == Commands.winner, state=GameStates.winner)
async def winner_button(callback_query: types.CallbackQuery, state: FSMContext):
    if all(total.values()):
        list_total_values = list(total.values())
        for player in players:
            if list_total_values[0] == list_total_values[1]:
                winner = Localization.draw_message.format(list_total_values[0])
            else:
                max_player_id = max(total, key=total.get)
                max_player_name = name[max_player_id]
                max_player_score = total[max_player_id]
                winner = Localization.winner_message.format(max_player_name, max_player_score)
            await bot.send_message(player, text=winner)
            await state.reset_state()
        players.clear()
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            Localization.show_winner, callback_data=Commands.winner))
        text = Localization.waiting_opponent
        await bot.send_message(chat_id=callback_query.message.chat.id, text=text, reply_markup=markup)


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    finally:
        bot.close()
        db.disconnect()
