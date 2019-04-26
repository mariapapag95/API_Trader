from flask import Flask, render_template, request, session, redirect, url_for
from model import User, Data

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def homepage():
    if request.method == 'GET':
        return render_template('homepage.html')
    elif request.method == 'POST':
        return render_template('homepage.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        u = User(username)
        users_balance = 100000
        if u.signup(username, password, confirm):  
            session["username"] = username  
            return render_template('dashboard.html', users_balance=users_balance)
        else:
            return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User(username)
        users_balance = u.user_balance()
        users_orders_info = u.user_orders()
        users_holdings_info = u.user_holdings()
        if u.login(password):
            session["username"] = username
            return render_template('dashboard.html',users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance)
        else:
            return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('homepage.html')
    elif request.method == 'POST':
        look_up_stock = request.form.get('look_up_stock')
        volume = request.form.get('volume')
        buy_stock = request.form.get('buy_stock')
        buy_volume = request.form.get('buy_volume')
        sell_stock = request.form.get('sell_stock')
        sell_volume = request.form.get('sell_volume')
        u = User(session["username"])
        users_balance = u.user_balance()
        users_orders_info = u.user_orders()
        users_holdings_info = u.user_holdings()
        data = Data()
        if volume:
            volume = int(volume)
            quote_results = data.quote(look_up_stock,volume)
            return render_template('dashboard.html', quote_results=quote_results,users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance)
        elif look_up_stock:
            lookup_results = data.lookup(look_up_stock)
            return render_template('dashboard.html', lookup_results=lookup_results,users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance)
        elif buy_stock:
            if u.buy(buy_stock,buy_volume):
                return render_template('dashboard.html', users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance)
                # This doesn't reload the page with latest data but the order goes through 
            else:
                return render_template('error.html')
        elif sell_stock:
            if u.sell(sell_stock,sell_volume):
                return render_template('dashboard.html', users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance)
                # This doesn't reload the page with latest data but the order goes through 
            else:
                return render_template('error.html')
        else:
            error_message = "Your order was not confirmed. Please try again."
            return render_template('dashboard.html',users_orders_info=users_orders_info,users_holdings_info=users_holdings_info,users_balance=users_balance,message=error_message)

@app.route('/close_account', methods=['GET','POST'])
def abort():
    if request.method == 'GET':
        return render_template('close.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User(session["username"])
        if u.delete_user(username):
            return redirect('/')
        else: 
            return render_template('error.html')

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    if request.method == 'GET':
        return render_template('adminlogin.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        adminkey = request.form['adminkey']
        d = Data()
        users = d.users()
        holdings = d.holdings()
        orders = d.orders()
        leaderboard = d.leaderboard()
        u = User(session["username"])
        if u.admin(password,adminkey):
            return render_template('admindashboard.html',users=users,holdings=holdings,orders=orders,leaderboard=leaderboard)
        else:
            return render_template('adminlogin.html')

@app.route('/super', methods=['GET','POST'])
def superuser():
    if request.method == 'GET':
        return render_template('secretlogin.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        superkey = request.form['superkey']
        d = Data()
        users = d.users()
        holdings = d.holdings()
        orders = d.orders()
        leaderboard = d.leaderboard()
        super_balance = 10000000000000
        u = User(session["username"])
        if u.superuser(password,superkey):
            return render_template('superuser.html',users=users,holdings=holdings,orders=orders,leaderboard=leaderboard,super_balance=super_balance)
        else:
            return render_template('secretlogin.html')

@app.route('/logout',methods=['POST'])
def logout():
    if request.method == 'POST':
        session.pop('username') 
        return render_template('homepage.html')


if __name__ == '__main__':
    app.secret_key = 'maria'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug = True)