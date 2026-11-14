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

    def get_dish(self, dish_id):
        # one dish as a dictionary, or None when the id is unknown
        sql = 'SELECT id, name, category, cost FROM dishes WHERE id = ?'
        conn = self.connect()
        try:
            row = conn.execute(sql, (dish_id,)).fetchone()
            return dict(row) if row else None
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

    def update_dish(self, dish_id, name, category, cost):
        # True when a row was changed, False when the id is unknown
        sql = 'UPDATE dishes SET name = ?, category = ?, cost = ? WHERE id = ?'
        conn = self.connect()
        try:
            with conn:
                cursor = conn.execute(sql, (name, category, cost, dish_id))
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_dish(self, dish_id):
        # True when a row was deleted, False when the id is unknown
        sql = 'DELETE FROM dishes WHERE id = ?'
        conn = self.connect()
        try:
            with conn:
                cursor = conn.execute(sql, (dish_id,))
            return cursor.rowcount > 0
        finally:
            conn.close()

    def total_cost(self):
        # the sum of all costs, and 0 when the list is empty
        sql = 'SELECT COALESCE(SUM(cost), 0) FROM dishes'
        conn = self.connect()
        try:
            return conn.execute(sql).fetchone()[0]
        finally:
            conn.close()
