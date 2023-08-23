from flask import Flask, g, redirect, render_template, request, url_for, make_response
from argparse import ArgumentParser
import os, random
import sqlite3

IMAGES_BASE_URL = "https://turbina.gsd.inesc-id.pt/csf2324/t1/images"
DB_PATH = "sqlite.db"


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User: {self.username}>"

# Storing users and passwords like this is obviously
# not secure at all, but it's just a demo :)
users = []
users.append(User(username="admin", password="str0ng3stP@ssw0rd"))
users.append(User(username="student", password="123456789"))
users.append(User(username="teacher", password="987654321"))
users.append(User(username="guest", password="guest"))


def get_user_by_username(username: str):
    for u in users:
        if u.username == username:
            return u
    return None


def check_login(username, password):
    for u in users:
        if u.username == username and u.password == password:
            return True
    return False


def create_token(username):
    token = os.urandom(64).hex()
    insert_token(token, username)
    return token


def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    res = cursor.execute("SELECT name FROM sqlite_master WHERE name='tokens'")
    if not res.fetchone():
        cursor.execute("CREATE TABLE tokens (token TEXT, username TEXT)")
        conn.commit()
    conn.close()


def get_user_by_token(token):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    res = cursor.execute("SELECT username FROM tokens WHERE token=?", (token,))
    res = res.fetchone()
    conn.close()
    if res:
        return get_user_by_username(res[0])
    else:
        return None


def insert_token(token, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tokens VALUES (?, ?)", (token, username))
    conn.commit()
    conn.close()


def delete_token(token):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tokens WHERE token=?", (token,))
    conn.commit()
    conn.close()


bgs = []
for filename in os.listdir("images/coffee"):
    bgs.append(os.path.join(IMAGES_BASE_URL, "images", "coffee", filename))

setup_db()
app = Flask(__name__)
app.secret_key = "rDizfC7@pXXv!5ioK3&kz67CAUgsNtUvn7f7%$TFnmyuhKSKooX7N9uy7"


@app.before_request
def before_request():
    g.error = ""
    g.token = request.cookies.get("token")
    if g.token:
        g.user = get_user_by_token(g.token)
    else:
        g.user = None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if check_login(username, password):
            resp = make_response(redirect(url_for("profile")))
            resp.set_cookie("token", create_token(username), max_age=5 * 60)
            return resp
        else:
            return redirect(url_for("login"))
    else:
        if g.user:
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", bg_url=os.path.join(IMAGES_BASE_URL, "images", "login.jpg"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        delete_token(g.token)
        resp = make_response(redirect(url_for("login")))
        resp.delete_cookie("token")
        return resp
    else:
        if g.user:
            return render_template("profile.html", bg_url=random.choice(bgs), username=g.user.username)
        else:
            return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    if not g.user:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("profile"))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", default=8000, type=int, help="port to listen on")
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port)
