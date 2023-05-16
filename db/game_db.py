# Initialize SQLite database connection
import sqlite3

class SQLiteDB:

    games_table = "games"
    sessions_table = "sessions"
    players_table = "players"

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Connected to SQLite database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print(f"Disconnected from SQLite database: {self.db_name}")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    def fetch_data(self, query):
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return []

    def create_table(self, table_name, columns):
        try:
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.execute_query(create_query)
            print(f"Table '{table_name}' created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, table_name, user_id, user_name, dice_value):
        try:
            insert_query = f"INSERT INTO {table_name} VALUES {user_id, user_name, dice_value}"
            self.execute_query(insert_query)
            print("Data inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}") 
            
    def update_game(self):
        try:
            print("TODO UPDATE GAME")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
    
    def update_session(self):
        try:
            print("TODO UPDATE SESSION")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def update_player(self):
        try:
            print("UPDATE PLAYERS DATA")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def init_game_table(self):
        self.create_table(self.games_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          player_id INTEGER NOT NULL,
                          session_id INTEGER NOT NULL,
                          result INTEGER NOT NULL,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (player_id) REFERENCES players (player_id),
                          FOREIGN KEY (session_id) REFERENCES game_sessions (session_id)
                          ''')
        self.create_table(self.sessions_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          winner_id INTEGER,
                          score INTEGER,
                          start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          end_time TIMESTAMP
                          ''')
        self.create_table(self.players_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          player_id INTEGER NOT NULL,
                          player_name STRING,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          ''')
    
    def insert_game_result(self, user_id, user_name, dice_value):
        self.insert_data(self.games_table, user_id, user_name, dice_value)

    def fetch_all_data(self):
        rows = self.fetch_data(f"SELECT * FROM {self.games_table}")
        for row in rows:
            print(row)
        return rows
