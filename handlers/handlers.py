from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from gameplay.game_state import GameState
from helpers.helpers import add_new_player, send_roll_result, send_start_game_message, update_total_and_send_result, send_again_game_message
from resources.localization import Localization
from resources.commands import *
from gameplay.states import GameStates
from config import NUM_PLAYERS, NUM_ROLLS
from bot_setup import bot
from gameplay.game_state import players, rolls, total, name


def setup_handlers(dp):
    dp.message_handler(Command(start))(cmd_start)
    dp.callback_query_handler(is_play, state=GameStates.play)(play_button)
    dp.callback_query_handler(
        is_roll_dice, state=GameStates.rolls)(roll_dice_button)
    dp.callback_query_handler(is_again, state=GameStates.rolls)(again_button)


def is_play(callback_query: types.CallbackQuery):
    return callback_query.data == play


def is_roll_dice(callback_query: types.CallbackQuery):
    return callback_query.data == GameState.ROLL_DICE


def is_again(callback_query: types.CallbackQuery):
    return callback_query.data == again


async def check_and_add_player(message, user_id, user_name):
    if len(players) >= NUM_PLAYERS:
        text = Localization.sorry
        await message.reply(text)
    else:
        if user_id not in players:
            await add_new_player(user_id, user_name)


async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    await check_and_add_player(message, user_id, user_name)
    await send_start_game_message(message)
    await GameStates.play.set()


async def again_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await check_and_add_player(callback_query, user_id, user_name)
    await send_again_game_message(callback_query)
    await GameStates.play.set()


async def play_button(callback_query: types.CallbackQuery, state: FSMContext):
    if len(players) != NUM_PLAYERS:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.waiting)
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=Localization.lets_play.format(NUM_ROLLS), reply_markup=GameState())
        await GameStates.rolls.set()

async def roll_dice_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    if len(rolls[user_id]) == NUM_ROLLS:
        await update_total_and_send_result(callback_query, user_id)
        await winner_update(callback_query.message.chat.id, state)
    else:
        dice_roll = await bot.send_dice(chat_id=callback_query.message.chat.id)
        dice_roll_value = dice_roll["dice"]["value"]
        rolls[user_id].append(dice_roll_value)
        await send_roll_result(callback_query, user_id, dice_roll_value)


async def winner_update(chat_id, state: FSMContext):
    if all(total.values()):
        list_total_values = list(total.values())
        for player in players:
            if list_total_values[0] == list_total_values[1]:
                winner_session = Localization.draw_message.format(
                    list_total_values[0])
            else:
                max_player_id = max(total, key=total.get)
                max_player_name = name[max_player_id]
                max_player_score = total[max_player_id]
                winner_session = Localization.winner_message.format(
                    max_player_name, max_player_score)
                
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(Localization.play_again, callback_data=again))
            await bot.send_message(player, text=winner_session, reply_markup=markup)
        players.clear()
    else:
        text = Localization.waiting_opponent
        await bot.send_message(chat_id=chat_id, text=text)
