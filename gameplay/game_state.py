from aiogram.types import InlineKeyboardButton
from aiogram import types

# Game states

class GameState(types.InlineKeyboardMarkup):
    ROLL_DICE = 'roll_dice'
    START_GAME = 'start game'

    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton(
            'Roll Dice', callback_data=self.ROLL_DICE))
        
    def play_button(self):   
        self.add(InlineKeyboardButton(
            'Start Game', callback_data=self.START_GAME))