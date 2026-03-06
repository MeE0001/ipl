from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

FILE = "players.xlsx"


def load_players():
    return pd.read_excel(FILE, engine="openpyxl")

def save_players(df):
    df.to_excel(FILE, index=False)


@app.route("/")
def index():
    players = load_players()
    return render_template("index.html", players=players.to_dict(orient="records"))


@app.route("/search")
def search():
    country = request.args.get("country")

    df = load_players()

    if country:
        df = df[df["country"].str.lower() == country.lower()]

    return df.to_json(orient="records")


@app.route("/player/<int:pid>")
def player(pid):
    df = load_players()
    player = df[df["player_id"] == pid].iloc[0]

    return render_template("auction.html", player=player)


@app.route("/bid", methods=["POST"])
def bid():

    data = request.json

    pid = data["player_id"]
    bid = int(data["bid"])

    df = load_players()

    player = df[df["player_id"] == pid]

    current = int(player["current_bid"].values[0])

    if bid <= current:
        return jsonify({"status": "Bid must be higher"})

    now = datetime.now()

    df.loc[df.player_id == pid, "current_bid"] = bid
    df.loc[df.player_id == pid, "last_bid_time"] = now

    save_players(df)

    return jsonify({"status": "success"})


@app.route("/check_auction/<int:pid>")
def check(pid):

    df = load_players()

    player = df[df.player_id == pid].iloc[0]

    last = player["last_bid_time"]

    if pd.isna(last):
        return jsonify({"status": "active"})

    last = pd.to_datetime(last)

    diff = (datetime.now() - last).seconds

    if diff > 300:
        return jsonify({"status": "closed"})

    return jsonify({"status": "active"})


if __name__ == "__main__":
    app.run(debug=True)