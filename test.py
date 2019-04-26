from mapper import Database
import wrapper
import sqlite3
import time


def leaderboard():
    with Database() as db:
        db.cursor.execute('''SELECT * FROM leaderboard;''')
        leaderboard = db.cursor.fetchall()
        return leaderboard


print(leaderboard())