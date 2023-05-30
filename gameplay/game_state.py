from aiogram.types import InlineKeyboardButton
from aiogram import types
from resources.commands import again, roll_dice, play
import resources.localization 
# Game states


players = []
rolls = {}
total = {}
name = {}


class GameState(types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton(
            resources.localization.Localization.roll, callback_data=roll_dice))


class StartGameState(types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton(
            resources.localization.Localization.start_game, callback_data=play))
        

class PlayAgainState(types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(InlineKeyboardButton(
            resources.localization.Localization.play_again, callback_data=again))
