from db.game_db import SQLiteDB

db = SQLiteDB("game.db")
db.connect()
db.init_game_table()
