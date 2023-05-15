# Initialize SQLite database connection
import sqlite3

class SQLiteDB:

    games_table = "games"

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

    def insert_data(self, table_name, values):
        try:
            insert_query = f"INSERT INTO {table_name} VALUES {values}"
            self.execute_query(insert_query)
            print("Data inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
    
    def init_game_table(self):
        self.create_table(self.games_table,
                          '''
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          player_id INTEGER,
                          player_name STRING,
                          dice_value LIST,
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          ''')
    
    def insert_game_result(self, values):
        self.insert_data(self.games_table, values)

    def fetch_all_data(self):
        rows = self.fetch_data(f"SELECT * FROM {self.games_table}")
        for row in rows:
            print(row)
        return rows
