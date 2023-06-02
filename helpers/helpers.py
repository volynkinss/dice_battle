from config import NUM_ROLLS
from resources.localization import Localization
from bot_setup import bot
from gameplay.game_state import GameState, StartGameState, players, rolls, total, name
from resources.commands import *


async def add_new_player(user_id: int, user_name: str):
    players.append(user_id)
    rolls.update({user_id: []})
    total.update({user_id: []})
    name.update({user_id: user_name})


async def send_start_game_message(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text=Localization.lets_play.format(NUM_ROLLS),
        reply_markup=StartGameState(),
    )


async def send_roll_result(chat_id, user_id: int, dice_roll_value: int):
    result = Localization.dice_result.format(
        len(rolls[user_id]), name[user_id], dice_roll_value
    )
    await bot.send_message(chat_id=chat_id, text=result, reply_markup=GameState())


async def update_total_and_send_result(chat_id, user_id: int):
    total_result = sum(rolls[user_id])
    result = Localization.total_result.format(NUM_ROLLS, name[user_id], total_result)
    total.update({user_id: total_result})
    await bot.send_message(chat_id=chat_id, text=result)


async def send_player_address_request(chat_id):
    await bot.send_message(chat_id=chat_id, text=Localization.address_request)
