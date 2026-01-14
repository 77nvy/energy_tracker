from flask import Flask, render_template, request, redirect, session, abort
import sqlite3

app = Flask(__name__)
app.secret_key = "SECRET123"  # Change in production


# ---------- DB Helpers ----------
def get_db():
    db = app.config.get("DATABASE", "energy_database.db")
    conn = sqlite3.connect(db, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


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

    # Products table (FIXED)
    c.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,              -- e.g. 'solar'
        name TEXT NOT NULL,                     -- e.g. 'Solar Panels'
        short_desc TEXT NOT NULL,               -- card summary
        long_desc TEXT NOT NULL,                -- full page text
        benefits TEXT NOT NULL,                 -- bullet points stored as text
        typical_saving_pct REAL DEFAULT 0.0      -- optional: used by calc logic later
    )
    """)

    conn.commit()
    conn.close()


def seed_products():
    """Insert the 3 Rolsa products if they don't exist."""
    conn = get_db()
    c = conn.cursor()

    products = [
        {
            "slug": "solar",
            "name": "Solar Panels",
            "short_desc": "Generate clean electricity from sunlight and reduce grid usage.",
            "long_desc": (
                "Solar panels convert sunlight into electricity for your home. "
                "This reduces the amount of electricity you need to buy from the grid, "
                "which can lower both costs and carbon footprint."
            ),
            "benefits": "• Reduce electricity bills\n• Lower carbon footprint\n• Works well with home batteries",
            "typical_saving_pct": 0.25
        },
        {
            "slug": "ev-charger",
            "name": "EV Charging Station",
            "short_desc": "Charge your electric vehicle at home safely and efficiently.",
            "long_desc": (
                "A dedicated EV charging station provides safer, faster charging than a standard plug. "
                "Smart chargers can schedule charging for off-peak times and track energy used for EV charging."
            ),
            "benefits": "• Faster charging\n• Potential off-peak savings\n• Track EV energy usage",
            "typical_saving_pct": 0.05
        },
        {
            "slug": "smart-home",
            "name": "Smart Home Energy Management",
            "short_desc": "Monitor and reduce energy use using automation and smart controls.",
            "long_desc": (
                "Smart home energy management can reduce wasted energy using automation, scheduling, "
                "and monitoring. Examples include smart thermostats, smart plugs, and device usage reports."
            ),
            "benefits": "• Reduce wasted energy\n• Better control of heating and appliances\n• Usage tracking and insights",
            "typical_saving_pct": 0.08
        }
    ]

    for p in products:
        c.execute("""
            INSERT OR IGNORE INTO products (slug, name, short_desc, long_desc, benefits, typical_saving_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (p["slug"], p["name"], p["short_desc"], p["long_desc"], p["benefits"], p["typical_saving_pct"]))

    conn.commit()
    conn.close()


# ---------- Routes ----------
@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute("SELECT slug, name, short_desc FROM products ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", products=rows)

@app.route("/register", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        c = db.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES(?,?)", (username, password))
            db.commit
            db.close
        except:
            return "Error: user already exists."
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    c = db.cursor()
    c.execute("")

@app.route("/product/<slug>")
def product(slug):
    """Shows one product page."""
    conn = get_db()
    row = conn.execute(
        "SELECT slug, name, short_desc, long_desc, benefits, typical_saving_pct FROM products WHERE slug = ?",
        (slug,)
    ).fetchone()
    conn.close()

    if row is None:
        abort(404)

    # convert bullet text into a Python list for easy looping
    benefits_list = [b.strip("• ").strip() for b in row["benefits"].split("\n") if b.strip()]
    return render_template("product.html", product=row, benefits=benefits_list)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    init_db()
    seed_products()
    app.run(debug=True)
