# Initialize SQLite database connection
import sqlite3
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s')

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
            logging.info(f"Connected to SQLite database: {self.db_name}")
        except sqlite3.Error as e:
            logging.info(f"Error connecting to SQLite database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logging.info(f"Disconnected from SQLite database: {self.db_name}")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            logging.info("Query executed successfully")
        except sqlite3.Error as e:
            logging.info(f"Error executing query: {e}")

    def fetch_data(self, query):
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            logging.info(f"Error fetching data: {e}")
            return []

    def create_table(self, table_name, columns):
        try:
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.execute_query(create_query)
            logging.info(f"Table '{table_name}' created successfully")
        except sqlite3.Error as e:
            logging.info(f"Error creating table: {e}")

    def create_player(self, user_id, user_name):
        try:
            insert_query = f"INSERT INTO {self.players_table} VALUES {user_id, user_name}"
            self.execute_query(insert_query)
            logging.info("Data inserted successfully")
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}") 

    def create_session(self):
        try:
            insert_query = f"INSERT INTO {self.sessions_table} VALUES {0, 0}"
            self.execute_query(insert_query)
            logging.info("Data inserted successfully")
            return self.get_last_session_id()
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}") 


    def create_game(self, player_id, session_id):
        try:
            insert_query = f"INSERT INTO {self.games_table} VALUES {player_id, session_id, 0}"
            self.execute_query(insert_query)
            logging.info("Data inserted successfully")
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}")


    def get_last_session_id(self):
        try:
            insert_query = f"SELECT id FROM {self.sessions_table} ORDER BY id DESC LIMIT 1"
            return self.execute_query(insert_query)            
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}") 

            
    def update_game(self):
        try:
            logging.info("TODO UPDATE GAME")
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}")
    
    def update_session(self):
        try:
            logging.info("TODO UPDATE SESSION")
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}")

    def update_player(self):
        try:
            logging.info("UPDATE PLAYERS DATA")
        except sqlite3.Error as e:
            logging.info(f"Error inserting data: {e}")

    def drop_table(self, table_name):
        try:
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name} has been dropped successfully.")
        except Exception as e:
            logging.info(f"An error occurred: {e}")

    def init_game_table(self):
        #drop
        self.drop_table(self.games_table)
        self.drop_table(self.sessions_table)
        self.drop_table(self.players_table)
        #init
        self.create_table(self.sessions_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          winner_id INTEGER,
                          score INTEGER,
                          end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          ''')
        self.create_table(self.players_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          player_id INTEGER NOT NULL,
                          player_name STRING,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          ''')
        
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
       
    
    def insert_game_result(self, user_id, user_name, dice_value):
        self.insert_data(self.games_table, user_id, user_name, dice_value)

    def fetch_all_data(self):
        rows = self.fetch_data(f"SELECT * FROM {self.games_table}")
        for row in rows:
            logging.info(row)
        return rows
