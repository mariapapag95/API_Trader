import sqlite3

connection = sqlite3.connect('master.db', check_same_thread=False)
cursor = connection.cursor()


# Users table
cursor.execute('''CREATE TABLE users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR DEFAULT 'Update Me',
    last_name VARCHAR DEFAULT 'Update Me',
    username VARCHAR UNIQUE,
    password VARCHAR DEFAULT 'Update Me',
    balance FLOAT DEFAULT '100000.00',
    portfolio_value FLOAT '100000.00,
    email VARCHAR DEFAULT 'Update Me',
    address VARCHAR DEFAULT 'Update Me',
    country VARCHAR DEFAULT 'Update Me',
    state VARCHAR DEFAULT 'Update Me',
    zip_ VARCHAR DEFAULT 'Update Me', 
    permission VARCHAR DEFAULT 'user'
    );''')


# Orders table
cursor.execute('''CREATE TABLE orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_type TEXT,
    ticker_symbol VARCHAR,
    last_price FLOAT,
    trade_volume INTEGER,
    order_cost FLOAT,
    unix_time FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(pk)
    );''')

# Holdings table
cursor.execute('''CREATE TABLE holdings(
    holding_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    ticker_symbol VARCHAR,
    VWAP FLOAT,
    trade_volume INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(pk)
    );''')

# Leaderboard table
cursor.execute('''CREATE TABLE leaderboard(
    pk INTEGER PRIMARY KEY,
    user_id INTEGER,
    portfolio_value FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(pk)
    );''')

connection.commit()
cursor.close()