import os
import sqlite3

# the database file sits next to this program
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iftar.db')


class DishDatabase:
    """All the SQLite work of the project is in this class."""

    def __init__(self, path=DB_FILE):
        self.path = path
        self.create_tables()

    def connect(self):
        # every operation opens its own connection
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        # creates the table only if it is missing, so old records stay
        sql = '''CREATE TABLE IF NOT EXISTS dishes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     category TEXT NOT NULL,
                     cost REAL NOT NULL)'''
        conn = self.connect()
        try:
            with conn:
                conn.execute(sql)
        finally:
            conn.close()

    def all_dishes(self):
        # a list of dictionaries, one for each saved dish
        sql = 'SELECT id, name, category, cost FROM dishes ORDER BY id'
        conn = self.connect()
        try:
            rows = conn.execute(sql).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def add_dish(self, name, category, cost):
        # the placeholders (?) keep the values out of the SQL text
        sql = 'INSERT INTO dishes (name, category, cost) VALUES (?, ?, ?)'
        conn = self.connect()
        try:
            with conn:
                cursor = conn.execute(sql, (name, category, cost))
            return cursor.lastrowid
        finally:
            conn.close()
