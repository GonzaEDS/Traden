import requests
import json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# CoinMarketCap API data
from apidata import api_call_data

# for login required
from functools import wraps
# for money to long
from re import sub
from decimal import Decimal


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///traden.db")

# login required decorator


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# account
def account():

    account = '<a href="/login" class="get-started-btn scrollto" >Login</a>'
    if not session.get("user_id") is None:
        name = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]['username']
        account = f'<div class="btn-group"> <button type="button" class="btn btn-success dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" style="color: #ffc451; background-color: black; border-color: #ffc451f7;">{name}</button> <ul class="dropdown-menu"> <li><a class="dropdown-item" href="/myaccount">My Account</a></li><li><a class="dropdown-item" href="/wallet">Wallet</a></li><li><a class="dropdown-item" href="/history">History</a></li><li><hr class="dropdown-divider"></li><li><a class="dropdown-item" href="/logout">Logout</a></li></ul></div>'

    return account

# apology


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", top=code, bottom=(message), account=account()), code


@app.route("/")
# @login_required
def index():
    """Show portfolios of stocks"""
    # home
    return render_template('index.html', account=account())


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")
    else:
        # Validate submission
        name = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("confirmation")

        if not name:
            return apology("Unvalid Name")
        elif not password:
            return apology("Not Password Provided")
        elif not password2:
            return apology("Provide Password Confirmation")
        elif not password == password2:
            return apology("Passwords Don't Match")

        else:
            hashed = generate_password_hash(password)
            users = db.execute("SELECT * FROM users")
            for user in users:
                if name == user['username']:
                    return apology("Username Already Taken")

            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", name, hashed)

           # Remember which user has logged in
            rows = db.execute("SELECT * FROM users WHERE username = ?", name)
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            flash("This is the Dashboard. Here you can check coins prices. When you feel ready, go to \"buy | sell\" in the navigation bar to start your portfolio. You have $10,000 now. But you can add money from My Account if you want.")
            return redirect("/dashboard")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must Provide Username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must Provide Password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid Username and/or Password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    coins = api_call_data()

    coins_table_1 = []
    coins_table_2 = []

    for i in range(len(coins)):
        if i < len(coins)/2:
            coins_table_1.append(coins[i])
        else:
            coins_table_2.append(coins[i])

    return render_template('dashboard.html', coins1=coins_table_1, coins2=coins_table_2, account=account())


@app.route("/coin/<coin_symbol>")
def coin(coin_symbol):

    data = api_call_data()

    for coins in data:
        if coins['symbol'] == coin_symbol:
            coin_id = coins['id']
            break

    with open('info.txt') as json_file:
        info = json.load(json_file)

    info_request = info['data'][f'{coin_id}']

    return render_template('info.html', info=info_request, account=account())


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

    ########################
    # Buy or Sell
    ########################


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy an amount of cryptocurrency"""
    # Mostrar formulario

    user_id = session["user_id"]

    coins = api_call_data()
    coins_logos_dict = {}
    coins_prices_dict = {}
    coins_names_dict = {}

    for coin in coins:
        x = coin['symbol']
        price = Decimal(sub(r'[^\d.]', '', coin['price']))
        name = coin['name']
        logo = coin['logo']
        coins_logos_dict[x] = str(logo)
        coins_prices_dict[x] = str(price)
        coins_names_dict[x] = name

    wallet_symbol_dicts = db.execute("SELECT symbol FROM wallets WHERE user_id = ( ? )", session["user_id"])

    user_coins_list = []
    for coins in wallet_symbol_dicts:
        user_coins_list.append(coins['symbol'])

    user_cryptos = user_coins_list

    if request.method == "GET":

        return render_template("buy.html", coins=coins_prices_dict, user_cryptos=user_cryptos, account=account())
    #POST#
    else:

        buy_or_sell = request.form.get("btnradio")
        symbol = request.form.get("symbol")

        try:
            name = coins_names_dict[symbol]
        except (KeyError, TypeError, ValueError):
            name = 'dollars'

        try:
            float(request.form.get("quantityOutput"))
        except (KeyError, TypeError, ValueError):
            return apology("Monst Provide Quantity")

        user_coin = request.form.get("userCoin")

        quantity_output = float(request.form.get("quantityOutput"))

        usd_equivalent = float(request.form.get("usdEquivalent"))

        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']

        try:
            float(request.form.get("cryptos"))
            quantity_input = float(request.form.get("cryptos"))
        except (KeyError, TypeError, ValueError):
            return apology("invalid input")

    ########################
    # BUY
    ########################
        if buy_or_sell == "buy":

            try:
                coins_prices_dict[symbol]
            except (KeyError, TypeError, ValueError):
                return apology("That Cryptocurrency Does Not Exist")

            # si paga con USD

            if user_coin == "USD":
                if cash < quantity_output:
                    return apology("Insufficient Funds Available")

                abort = False
                for coin in user_coins_list:
                    if symbol == coin:
                        abort = True
                        break

                if abort == False:
                    db.execute("INSERT INTO wallets VALUES ( ?, ?, ?, ?)", user_id, symbol, name, 0)

                current_cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash'])
                updated_cash = current_cash - quantity_output

                db.execute("UPDATE users SET cash = ( ? ) WHERE id = ?", updated_cash, user_id)

                current_coins = db.execute("SELECT coins FROM wallets WHERE user_id = ? AND symbol = ?",
                                           user_id, symbol)[0]['coins']

                db.execute("UPDATE wallets SET coins = ? WHERE user_id = ? AND symbol = ?",
                           current_coins + quantity_input, user_id, symbol)

                # Update history
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?)", user_id, symbol,
                           quantity_input, f'{quantity_output} USD', time)

                # si paga con otra moneada
            else:
                if symbol == user_coin:
                    return apology("Introduce Diferent Coins")

                available_coins = db.execute("SELECT coins FROM wallets WHERE user_id = ? AND symbol = ?",
                                             user_id, user_coin)[0]['coins']
                if quantity_output > available_coins:
                    return apology("Insufficient Funds Available")

                abort = False
                for coin in user_coins_list:
                    if symbol == coin:
                        abort = True
                        break

                if abort == False:
                    db.execute("INSERT INTO wallets VALUES ( ?, ?, ?, ?)", user_id, symbol, name, 0)

                # update coins used to pay
                updated_available_coins = available_coins - quantity_output

                if updated_available_coins == 0:
                    db.execute("DELETE FROM wallets WHERE user_id = ? AND symbol = ?", user_id, user_coin)
                else:
                    db.execute("UPDATE wallets SET coins = ? WHERE user_id = ? AND symbol = ?",
                               updated_available_coins, user_id, user_coin)

                # update coins buyed
                current_coins = db.execute("SELECT coins FROM wallets WHERE user_id = ? AND symbol = ?",
                                           user_id, symbol)[0]['coins']

                db.execute("UPDATE wallets SET coins = ? WHERE user_id = ? AND symbol = ?",
                           current_coins + quantity_input, user_id, symbol)

                # Update history
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?)", user_id, symbol,
                           quantity_input, f'{quantity_output} {user_coin}', time)

    ########################
    # SELL
    ########################
        else:
            coins_to_sell = db.execute("SELECT coins FROM wallets WHERE user_id = ? AND symbol = ?",
                                       user_id, user_coin)[0]['coins']
            if coins_to_sell < quantity_input:
                return apology("Insufficient Funds Available")

            if symbol == user_coin:
                return apology("Introduce Diferent Coins")

            # update selled coins
            updated_coins_to_sell = coins_to_sell - quantity_input
            if updated_coins_to_sell == 0:
                db.execute("DELETE FROM wallets WHERE user_id = ? AND symbol = ?",
                           user_id, user_coin)
            else:
                db.execute("UPDATE wallets SET coins = ? WHERE user_id = ? AND symbol = ?",
                           updated_coins_to_sell, user_id, user_coin)

                # SI VENDE POR USD
            if symbol == 'USD':

                updated_cash = cash + quantity_output

                db.execute("UPDATE users SET cash = ( ? ) WHERE id = ?", updated_cash, user_id)

                # SI VENDE POR OTRA MONEDA
            else:

                try:
                    coins_prices_dict[symbol]
                except (KeyError, TypeError, ValueError):
                    return apology("That Cryptocurrency Does Not Exist")

                abort = False
                for coin in user_coins_list:
                    if symbol == coin:
                        abort = True
                        break

                if abort == False:
                    db.execute("INSERT INTO wallets VALUES ( ?, ?, ?, ?)", user_id, symbol, name, 0)

                coin_to_buy = db.execute("SELECT coins FROM wallets WHERE user_id = ? AND symbol = ?", user_id, symbol)[0]['coins']

                updated_coin_to_buy = coin_to_buy + quantity_output

                db.execute("UPDATE wallets SET coins = ? WHERE user_id = ? AND symbol = ?",
                           updated_coin_to_buy, user_id, symbol)

            # Update history
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?)", user_id, user_coin,
                       -quantity_input, f'{quantity_output} {symbol}', time)

            # test line
            # return render_template("test.html", this=db.execute("SELECT * FROM wallets WHERE user_id = ?", user_id), thistoo=db.execute("SELECT * FROM users WHERE id = ?", user_id), also=db.execute("SELECT * FROM history WHERE user_id = ?", user_id))

        # Create dictionary for wallet
        user_wallet = db.execute("SELECT * FROM wallets WHERE user_id = ?", user_id)
        TOTAL_USD = 0
        for dicts in user_wallet:

            symbol = dicts['symbol']
            logo = coins_logos_dict[symbol]
            price = float(coins_prices_dict[symbol])
            dicts['logo'] = logo
            dicts['price'] = price
            usd_equiv = float(dicts['coins']) * price
            dicts['usd_equiv'] = usd_equiv
            TOTAL_USD += usd_equiv

        updated_cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash'])

        flash('Operation succeeded')
        return render_template("wallet.html", wallet=user_wallet, cash=updated_cash, total=TOTAL_USD+updated_cash, account=account())


@app.route("/wallet")
@login_required
def wallet():
    """Show portfolios of coins"""

    user_id = session["user_id"]

    coins = api_call_data()
    coins_logos_dict = {}
    coins_prices_dict = {}
    coins_names_dict = {}

    for coin in coins:
        x = coin['symbol']
        price = Decimal(sub(r'[^\d.]', '', coin['price']))
        name = coin['name']
        logo = coin['logo']
        coins_logos_dict[x] = str(logo)
        coins_prices_dict[x] = str(price)
        coins_names_dict[x] = name

    # Create dictionary for wallet
    user_wallet = db.execute("SELECT * FROM wallets WHERE user_id = ?", user_id)
    TOTAL_USD = 0

    for dicts in user_wallet:
        symbol = dicts['symbol']
        logo = coins_logos_dict[symbol]
        price = float(coins_prices_dict[symbol])
        dicts['logo'] = logo
        dicts['price'] = price
        usd_equiv = float(dicts['coins']) * price
        dicts['usd_equiv'] = usd_equiv
        TOTAL_USD += usd_equiv

    updated_cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash'])

    # home
    return render_template("wallet.html", wallet=user_wallet, cash=updated_cash, total=TOTAL_USD+updated_cash, account=account())


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])

    return render_template("history.html", history=history, account=account())


@app.route("/myaccount")
@login_required
def myaccount():
    """Show account data"""

    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
   # return render_template("test.html", this=user)
    return render_template("myaccount.html", users=user, account=account())


@app.route("/username", methods=["GET", "POST"])
@login_required
def username():
    """change username"""

    if request.method == "GET":
        return render_template("username.html", account=account())
    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide new username", 403)

        new_name = request.form.get("username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must Provide Password", 403)

        password = request.form.get("password")

        # New username dont exist
        users = db.execute("SELECT * FROM users")
        for user in users:
            if new_name == user['username']:
                return apology("Username Already Taken")

        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure password is correct
        if not check_password_hash(user[0]["hash"], request.form.get("password")):
            return apology("Invalid Password", 403)

        # Change username
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_name, session["user_id"])

        return redirect("/myaccount")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change Password"""

    if request.method == "GET":
        return render_template("password.html", account=account())
    else:
        # Validate submission
        password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must Provide Password", 403)
        elif not request.form.get("new_password"):
            return apology("Must Provide New Password", 403)
        elif not request.form.get("confirmation"):
            return apology("Must Provide Confirmation", 403)
        elif not new_password == confirmation:
            return apology("Passwords Don't Match")

        # Ensure password is correct
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(user[0]["hash"], request.form.get("password")):
            return apology("Invalid Password", 403)

        else:
            hashed = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed, session["user_id"])

            # Redirect user
            return redirect("/myaccount")


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("cash.html", account=account())

    else:
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
        requested = int(request.form.get("cash"))
        new_cash = cash + requested

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])
        return redirect("/myaccount")
