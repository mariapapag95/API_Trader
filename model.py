from mapper import Database
import wrapper
import sqlite3
import time
import random

class User:

    def __init__(self,username):
        self.username = username
        self.api_key = random.randrange(1000000000,9999999999)


    def __enter__(self):
        return self

    def __exit__(self,type,value,traceback):
        pass
        #TODO

    def signup(self, username, password, confirm):
    # Will create new user if username is not already in use (SQL UNIQUE in db) AND if user inputs password correctly (twice)
        try:
            if password == confirm:
                with Database() as db:
                    db.cursor.execute('''INSERT INTO users (
                                    username,
                                    password)
                                    VALUES(?,?);''',
                                    (username,password))
                    return True
            else:
                return False
        except:
            if sqlite3.IntegrityError:
                return False

    def login(self, password):
    # Will check if username exists, 
    # then if password input matches password in db
        with Database() as db:
            db.cursor.execute('''SELECT password FROM users WHERE username="{username}";'''
                .format(username=self.username))
            correct_password = db.cursor.fetchone()
            if correct_password is None:
                return False
            else:
                if correct_password[0] == password:
                    return True
                else:
                    return False

    def admin(self, password, adminkey):
    # Will check if username exists, 
    # then if password input matches password in db, 
    # then if admin key input is correct key ('admin'), 
    # then updates permission in users table in db from default 'user' to 'admin'
        with Database() as db:
            db.cursor.execute('''SELECT password FROM users WHERE username="{username}";'''
                .format(username=self.username))
            correct_password = db.cursor.fetchone()
            if correct_password is None:
                return False
            else:
                if correct_password[0] == password and adminkey == 'admin':
                    db.cursor.execute('''UPDATE users SET permission = "admin" WHERE username = "{username}";'''
                            .format(username=self.username))
                    return True
                else:
                    return False

    def superuser(self, password, superkey):
    # Will check if username exists, 
    # then if password input matches password in db, 
    # then if super key input is correct key ('super'), 
    # then updates permission in users table in db from default 'user' to 'super'
        with Database() as db:
            db.cursor.execute('''SELECT password FROM users WHERE username="{username}";'''
                .format(username=self.username))
            correct_password = db.cursor.fetchone()
            if correct_password is None:
                return False
            else:
                if correct_password[0] == password and superkey == 'super':
                    db.cursor.execute('''UPDATE users SET permission = "super" WHERE username = "{username}";'''
                            .format(username=self.username))
                    return True
                else:
                    return False

    def id_lookup(self,username):
    # Returns user_id according to username
        with Database() as db:
            db.cursor.execute('''SELECT user_id FROM users WHERE "{}" = username;'''.format(self.username))
            user_id = db.cursor.fetchone()[0]
            return user_id

    def password_lookup(self):
        with Database() as db:
            db.cursor.execute('''SELECT password FROM users WHERE user_id={user_id};'''
                    .format(user_id = self.id_lookup(self.username)))
            user_password = db.cursor.fetchone()[0]
            return user_password

    def vwap(self,ticker_symbol):
        with Database() as db:
            db.cursor.execute('''SELECT last_price, trade_volume FROM orders WHERE ticker_symbol="{}";'''
                                .format(ticker_symbol))
            purchase_hist = db.cursor.fetchall()
            pxv = []
            volumes = []
            # IF "purchase_hist" RETURNS LIST OF TUPLES LIKE [(last_price,trade_volume),(last_price,trade_volume))]
            for purchase in purchase_hist:
                price = float(purchase[0])
                # "last_price" IS SET TO FLOAT IN SCHEMA (WILL THIS BE A PROBLEM?)
                volume = float(purchase [1])
                pxv.append(price * volume)
                volumes.append(volume)
            vwap = sum(pxv) / sum(volumes)
            return vwap

    def buy(self,ticker_symbol,trade_volume):
    # Will check if user has enough funds to make purchase
        last_price = wrapper.lastprice(ticker_symbol)
        brokerage_fee = 6.95
        buy_cost = (float(last_price) * float(trade_volume)) + brokerage_fee
        user_balance = self.user_balance()
        if float(user_balance) > float(buy_cost):
            with Database() as db:
                # Update balance
                new_balance = user_balance - buy_cost    
                db.cursor.execute('''UPDATE users SET balance = {} WHERE user_id = {user_id};'''
                        .format(new_balance, user_id = self.id_lookup(self.username)))
                # Update orders
                time_ = time.time()
                user_id = self.id_lookup(self.username)
                db.cursor.execute('''INSERT INTO orders (
                                user_id, 
                                order_type,
                                ticker_symbol, 
                                last_price,
                                trade_volume,
                                order_cost,
                                unix_time) 
                                VALUES(?,?,?,?,?,?,?);''',
                                (user_id, "Buy", ticker_symbol, last_price, trade_volume, buy_cost, time_))
                # Update holdings
                db.cursor.execute('''SELECT trade_volume FROM holdings WHERE ticker_symbol = "{}" and user_id = {user_id};'''
                        .format(ticker_symbol, user_id = self.id_lookup(self.username)))
                old_volume = db.cursor.fetchone()
                if old_volume is None:
                    db.cursor.execute('''INSERT INTO holdings (
                                user_id, 
                                ticker_symbol, 
                                vwap,
                                trade_volume) 
                                VALUES(?,?,?,?);''',
                                (user_id, ticker_symbol, last_price, trade_volume))
                    return True
                else:
                    new_volume = old_volume[0] + int(trade_volume)
                    db.cursor.execute('''UPDATE holdings SET trade_volume = {} WHERE user_id = {user_id} AND ticker_symbol = "{ticker_symbol}";'''
                            .format(new_volume, user_id = self.id_lookup(self.username), ticker_symbol=ticker_symbol))
                    db.cursor.execute('''UPDATE holdings SET VWAP = {} WHERE user_id = {user_id} AND ticker_symbol = "{ticker_symbol}";'''
                            .format(self.vwap(ticker_symbol), user_id = self.id_lookup(self.username), ticker_symbol=ticker_symbol))
                    return True
        else:
            return False
    
    def sell(self,ticker_symbol,trade_volume):
    # Will check if user has holding of that stock,
    # then will checck if user has enough volume to sell,
        with Database() as db:
            db.cursor.execute('''SELECT ticker_symbol FROM holdings WHERE user_id = "{user_id}";'''
                    .format(user_id = self.id_lookup(self.username)))
            user_stock = db.cursor.fetchone()[0]
            if user_stock is None:
                return False
            elif user_stock == ticker_symbol:
                db.cursor.execute('''SELECT trade_volume FROM holdings WHERE user_id = "{user_id}";'''
                        .format(user_id = self.id_lookup(self.username)))
                user_holdings = db.cursor.fetchone()[0]
                if float(user_holdings) >= float(trade_volume):
                    last_price = wrapper.lastprice(ticker_symbol)
                    brokerage_fee = 6.95
                    sell_cost = (float(last_price) * float(trade_volume)) - brokerage_fee
                    user_balance = self.user_balance()
                    user_id = self.id_lookup(self.username)
                    # Update balance
                    new_balance = user_balance + sell_cost
                    db.cursor.execute('''UPDATE users SET balance = {} WHERE user_id = {user_id};'''
                                .format(new_balance, user_id = self.id_lookup(self.username)))
                    # Update orders
                    time_ = time.time()
                    db.cursor.execute('''INSERT INTO orders (
                            user_id, 
                            order_type,
                            ticker_symbol, 
                            last_price,
                            trade_volume,
                            order_cost,
                            unix_time) 
                            VALUES(?,?,?,?,?,?,?);''',
                            (user_id, "Sell", ticker_symbol, last_price, trade_volume, sell_cost, time_))
                    # Update holdings
                    if float(user_holdings) == float(trade_volume):
                        db.cursor.execute('''DELETE FROM holdings WHERE user_id={user_id};'''
                                .format(user_id = self.id_lookup(self.username)))
                        return True
                    else:
                        new_volume = float(user_holdings) - float(trade_volume)
                        db.cursor.execute('''UPDATE holdings SET trade_volume = {} WHERE user_id = {user_id};'''
                            .format(new_volume, user_id = self.id_lookup(self.username)))
                        db.cursor.execute('''UPDATE holdings SET VWAP = {} WHERE user_id = {user_id};'''
                            .format(self.vwap(ticker_symbol), user_id = self.id_lookup(self.username)))
                        return True
            else:
                return False
        
    def user_balance(self):
        with Database() as db:
            db.cursor.execute('''SELECT balance FROM users WHERE user_id={user_id};'''
                    .format(user_id = self.id_lookup(self.username)))
            balance = db.cursor.fetchone()[0]
            profit = float(balance) - 100000
            portfolio_value = balance
            db.cursor.execute('''UPDATE users SET portfolio_value = {} WHERE user_id = {user_id};'''
                                .format(portfolio_value, user_id = self.id_lookup(self.username)))
            return float(balance)

    def user_holdings(self):
        with Database() as db:
            db.cursor.execute('''SELECT * FROM holdings WHERE user_id={user_id};'''
                    .format(user_id = self.id_lookup(self.username)))
            table_user_holdings = db.cursor.fetchall()
            return table_user_holdings

    def user_orders(self):
        with Database() as db:
            db.cursor.execute('''SELECT * FROM orders WHERE user_id={user_id};'''
                    .format(user_id = self.id_lookup(self.username)))
            table_user_orders = db.cursor.fetchall()
            return table_user_orders

    def delete_user(self):
        with Database() as db:
            db.cursor.execute('''DELETE FROM users WHERE username = "{}";'''
                    .format(self.username))
            return True

class Admin:

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self,type,value,traceback):
        pass
        #TODO

class Data:

    def __init__(self):
        pass
        
    def __enter__(self):
        return self

    def __exit__(self,type,value,traceback):
        pass

    def lookup(self,ticker_symbol):
        stats = wrapper.info(ticker_symbol)
        return stats

    def quote(self,ticker_symbol,trade_volume):
        last_price = wrapper.lastprice(ticker_symbol)
        brokerage_fee = 6.95
        buy_cost = (last_price * trade_volume) + brokerage_fee
        return buy_cost

    def users(self):
        with Database() as db:
            db.cursor.execute('''SELECT * FROM users;''')
            table_users = db.cursor.fetchall()
            return table_users

    def orders(self):
        with Database() as db:
            db.cursor.execute('''SELECT * FROM orders ORDER BY unix_time DECS;''')
            table_orders = db.cursor.fetchall()
            return table_orders

    def holdings(self):
        with Database() as db:
            db.cursor.execute('''SELECT * FROM holdings ORDER BY ticker_symbol DECS;''')
            table_holdings = db.cursor.fetchall()
            return table_holdings

    def leaderboard(self):
        with Database() as db:
            db.cursor.execute('''SELECT user_id, portfolio_value FROM users ORDER BY portfolio_value DECS;''')
            leaderboard = db.cursor.fetchall()
            return leaderboard