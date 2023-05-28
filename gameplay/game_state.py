from aiogram.types import InlineKeyboardButton
from aiogram import types

# Game states


players = []
rolls = {}
total = {}
name = {}


class GameState(types.InlineKeyboardMarkup):
    ROLL_DICE = 'roll_dice'

    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton(
            'Roll Dice', callback_data=self.ROLL_DICE))