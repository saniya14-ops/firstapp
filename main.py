from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import config

app = Flask(__name__)

# --- SESSION CONFIG ---
app.secret_key = config.SECRET_KEY
# For local dev, do not enforce secure cookies
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"


# --- DATABASE CONNECTION ---
def get_db():
    """Get SQLite connection"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# --- CREATE TABLE ---
def create_table():
    """Create visitors table if it does not exist"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                purpose TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)

create_table()


# --- HOME PAGE (LOGIN) ---
@app.route("/")
def home():
    return render_template("login.html")


# --- LOGIN ---
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    # Simple validation
    if not username or not password:
        flash("Please enter username and password")
        return redirect(url_for("home"))

    # ADMIN LOGIN
    if username == config.USERNAME_ADMIN and password == config.PASSWORD_ADMIN:
        session["user"] = username
        session["role"] = "admin"
        return redirect(url_for("dashboard"))

    # GUARD LOGIN
    elif username == config.USERNAME_GUARD and password == config.PASSWORD_GUARD:
        session["user"] = username
        session["role"] = "guard"
        return redirect(url_for("dashboard"))

    else:
        flash("Invalid username or password")
        return redirect(url_for("home"))


# --- DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    with get_db() as conn:
        visitors = conn.execute("SELECT * FROM visitors ORDER BY id DESC").fetchall()

    return render_template("dashboard.html", visitors=visitors, role=session["role"])


# --- ADD VISITOR ---
@app.route("/add", methods=["POST"])
def add_visitor():
    if "user" not in session:
        return redirect(url_for("home"))

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    purpose = request.form.get("purpose", "").strip()

    # --- VALIDATION ---
    if not name or not phone or not purpose:
        flash("All fields are required")
        return redirect(url_for("dashboard"))

    if len(phone) != 10 or not phone.isdigit():
        flash("Phone number must be 10 digits")
        return redirect(url_for("dashboard"))

    # Auto timestamp
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO visitors (name, phone, purpose, time) VALUES (?, ?, ?, ?)",
            (name, phone, purpose, time)
        )

    flash("Visitor added successfully")
    return redirect(url_for("dashboard"))


# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# --- RUN APP ---
if __name__ == "__main__":
    app.run(debug=True)
