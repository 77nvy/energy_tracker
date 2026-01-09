from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "SECRET123"   # Change this in production
# Helper: get database connection
def get_db():
    # Make sure we get the DB name by checking the config for a DATABASE or assigning it a default one
    db = app.config.get("DATABASE", "energy_database.db") 
    return sqlite3.connect(db, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    init_db()
    #app.run(host='0.0.0.0', port=5000, debug=True)

    app.run(debug=True)