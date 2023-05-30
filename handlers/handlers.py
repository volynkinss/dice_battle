from aiogram import types
from aiogram.dispatcher.filters import Command
from gameplay.game_state import GameState, PlayAgainState
from helpers.helpers import *
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
    return callback_query.data == roll_dice


def is_again(callback_query: types.CallbackQuery):
    return callback_query.data == again


async def check_and_add_player(chat_id, user_id, user_name):
    if len(players) >= NUM_PLAYERS:
        await bot.send_message(chat_id=chat_id, text=Localization.sorry)
    else:
        if user_id not in players:
            await add_new_player(user_id, user_name)


async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    chat_id = message.chat.id
    await check_and_add_player(chat_id, user_id, user_name)
    await send_start_game_message(chat_id)
    await GameStates.play.set()


async def again_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.username
    chat_id = callback_query.message.chat.id
    await check_and_add_player(chat_id, user_id, user_name)
    await send_start_game_message(chat_id)
    await GameStates.play.set()


async def play_button(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    if len(players) > NUM_PLAYERS:
        raise(Exception('fatal num players in session'))
    if len(players) != NUM_PLAYERS:
        await bot.send_message(chat_id=chat_id, text=Localization.waiting)
    else:
        await GameStates.rolls.set()
        for player_id in players:
            if player_id == chat_id:
                continue
            await bot.send_message(chat_id=player_id, text=Localization.found_opponent)
        await bot.send_message(chat_id=chat_id, text=Localization.lets_play.format(NUM_ROLLS), reply_markup=GameState())

    

async def roll_dice_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    if len(rolls[user_id]) < NUM_ROLLS:
        dice_roll = await bot.send_dice(chat_id=chat_id)
        dice_roll_value = dice_roll["dice"]["value"]
        rolls[user_id].append(dice_roll_value)
        await send_roll_result(chat_id, user_id, dice_roll_value)
    if len(rolls[user_id]) == NUM_ROLLS:
        await update_total_and_send_result(chat_id, user_id)
        await winner_update(chat_id)


async def winner_update(chat_id):
    if all(total.values()):
        list_total_values = list(total.values())
        for player_id in players:
            if list_total_values[0] == list_total_values[1]:
                winner_session = Localization.draw_message.format(
                    list_total_values[0])
            else:
                max_player_id = max(total, key=total.get)
                max_player_name = name[max_player_id]
                max_player_score = total[max_player_id]
                winner_session = Localization.winner_message.format(
                    max_player_name, max_player_score)
                
            await bot.send_message(player_id, text=winner_session, reply_markup=PlayAgainState())
        players.clear()
    else:
        await bot.send_message(chat_id=chat_id, text=Localization.waiting_opponent)
