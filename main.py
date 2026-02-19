from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS visitors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        flat TEXT,
        purpose TEXT,
        vehicle TEXT,
        entry_time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN PAGE ----------------

@app.route("/")
def home():
    return render_template("login.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["user"] = username
        session["role"] = "admin"
        return redirect("/dashboard")

    elif username == "guard" and password == "1234":

        session["user"] = username
        session["role"] = "guard"
        return redirect("/dashboard")

    else:
        return "Invalid Login"

# ---------------- DASHBOARD ----------------

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        flat = request.form["flat"]
        purpose = request.form["purpose"]
        vehicle = request.form["vehicle"]

        entry_time = datetime.now().strftime("%d-%m-%Y %H:%M")

        c.execute("INSERT INTO visitors(name,phone,flat,purpose,vehicle,entry_time) VALUES(?,?,?,?,?,?)",
                  (name,phone,flat,purpose,vehicle,entry_time))

        conn.commit()

    conn.close()

    return render_template("dashboard.html", role=session["role"])

# ---------------- HISTORY PAGE ----------------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM visitors ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    return render_template("history.html",
                           data=data,
                           role=session["role"])

# ---------------- DELETE ----------------

@app.route("/delete/<int:id>")
def delete(id):

    if session["role"] != "admin":
        return "Access Denied"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM visitors WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/history")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(app.run(host="0.0.0.0", port=5000, debug=True))
