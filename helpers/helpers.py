from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import NUM_ROLLS
from resources.localization import Localization
from bot_setup import bot
from gameplay.game_state import GameState, players, rolls, total, name
from resources.commands import *

async def add_new_player(user_id: int, user_name: str):
    players.append(user_id)
    rolls.update({user_id: []})
    total.update({user_id: []})
    name.update({user_id: user_name})


async def send_start_game_message(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(Localization.start_game,
                                 callback_data=play)
        ]
    ])
    await message.reply(Localization.lets_play.format(NUM_ROLLS), reply_markup=markup)


async def send_again_game_message(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(Localization.start_game,
                                 callback_data=play)
        ]
    ])
    await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.lets_play.format(NUM_ROLLS), reply_markup=markup)

async def send_roll_result(callback_query: types.CallbackQuery, user_id: int, dice_roll_value: int):
    result = Localization.dice_result.format(
        len(rolls[user_id]), name[user_id], dice_roll_value)
    await bot.send_message(chat_id=callback_query.message.chat.id, text=result, reply_markup=GameState())


async def update_total_and_send_result(callback_query: types.CallbackQuery, user_id: int):
    total_result = sum(rolls[user_id])
    result = Localization.total_result.format(
        NUM_ROLLS, name[user_id], total_result)
    total.update({user_id: total_result})
    await bot.send_message(chat_id=callback_query.message.chat.id, text=result)
