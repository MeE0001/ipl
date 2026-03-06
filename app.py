from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import pandas as pd
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

socketio = SocketIO(app)

FILE = "players.xlsx"


def load_players():
    return pd.read_excel(FILE)


def save_players(df):
    df.to_excel(FILE, index=False)


# LOGIN PAGE
@app.route("/")
def login_page():
    return render_template("login.html")


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
        cur.execute("INSERT INTO users VALUES (?,?)", (username, password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


# LOGIN CHECK
@app.route("/login", methods=["POST"])
def login_check():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    conn.close()

    if user:
        session["username"] = username
        return redirect("/auction")

    return "Invalid login"


# DASHBOARD
@app.route("/auction")
def auction():

    if "username" not in session:
        return redirect("/")

    players = load_players()

    return render_template(
        "index.html",
        players=players.to_dict(orient="records"),
        username=session["username"]
    )


# PLAYER AUCTION PAGE
@app.route("/player/<int:player_id>")
def player_page(player_id):

    if "username" not in session:
        return redirect("/")

    df = load_players()

    player = df[df["player_id"] == player_id].iloc[0].to_dict()

    return render_template(
        "player.html",
        player=player,
        username=session["username"]
    )


# LIVE BID SYSTEM
@socketio.on("bid")
def handle_bid(data):

    player = data["player"]
    price = int(data["price"])

    df = load_players()

    df.loc[df["name"] == player, "current_bid"] = price

    save_players(df)

    emit("update", data, broadcast=True)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

if __name__ == "__main__":
    socketio.run(app, debug=True)

