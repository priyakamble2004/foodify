import os
from functools import wraps

from flask import Flask, jsonify, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import Food, History, User, db
from seed_data import load_seed

app = Flask(__name__, static_folder="static", static_url_path="")

# ---------- Configuration (from environment variables) ----------
db_url = os.getenv("DATABASE_URL") or "sqlite:///foodify.db"
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
if db_url.startswith("mysql") and "charset" not in db_url:
    db_url += ("&" if "?" in db_url else "?") + "charset=utf8mb4"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
if db_url.startswith("mysql"):
    # Free hosted MySQL allows only a few connections, so keep the pool small.
    options = {"pool_size": 2, "max_overflow": 0, "pool_recycle": 280, "pool_pre_ping": True}
    # Many cloud MySQL services require an encrypted connection.
    if os.getenv("DB_SSL_CA"):                      # path to the provider's CA certificate (checks the server)
        options["connect_args"] = {"ssl": {"ca": os.getenv("DB_SSL_CA")}}
    elif os.getenv("DB_SSL") == "1":                # encrypt, without checking the server's certificate
        options["connect_args"] = {"ssl": {"fake_flag_to_enable_tls": True}}
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = options
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE") == "1"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 7  # 7 days

db.init_app(app)


def init_db():
    with app.app_context():
        db.create_all()
        load_seed()


init_db()


# ---------- Helpers ----------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(error="Please log in."), 401
        return fn(*args, **kwargs)
    return wrapper


# ---------- Pages ----------
@app.get("/")
@app.get("/index.html")
def home():
    if "user_id" not in session:
        return redirect("/login.html")
    return app.send_static_file("index.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login.html")


# ---------- Health ----------
@app.get("/api/health")
def health():
    # "database" shows which kind is in use, so you can tell if the cloud database is really connected.
    return jsonify(status="ok", database="mysql" if db_url.startswith("mysql") else "sqlite")


# ---------- Foods ----------
@app.get("/api/foods")
def foods():
    query = Food.query.order_by(Food.name)
    q = (request.args.get("q") or "").strip()
    if q:
        query = query.filter(Food.name.ilike("%" + q + "%"))
    return jsonify([f.to_dict() for f in query.all()])


@app.get("/api/foods/<food_id>")
def food(food_id):
    item = db.session.get(Food, food_id)
    if not item:
        return jsonify(error="Food not found."), 404
    return jsonify(item.to_dict())


# ---------- Accounts ----------
@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()[:30]
    password = data.get("password") or ""
    if not name:
        return jsonify(error="Enter your name."), 400
    if len(password) < 4:
        return jsonify(error="Password needs at least 4 characters."), 400
    key = name.lower()
    if User.query.filter_by(key=key).first():
        return jsonify(error="That name is taken. Log in, or pick another name."), 409
    user = User(name=name, key=key, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    session.clear()
    session.permanent = True
    session["user_id"] = user.id
    return jsonify(name=user.name), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    key = (data.get("name") or "").strip().lower()
    user = User.query.filter_by(key=key).first()
    if not user or not check_password_hash(user.password_hash, data.get("password") or ""):
        return jsonify(error="Name or password is incorrect."), 401
    session.clear()
    session.permanent = True
    session["user_id"] = user.id
    return jsonify(name=user.name)


@app.get("/api/me")
@login_required
def me():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return jsonify(error="Please log in."), 401
    return jsonify(name=user.name)


# ---------- History ----------
@app.get("/api/history")
@login_required
def history_list():
    rows = (History.query.filter_by(user_id=session["user_id"])
            .order_by(History.id.desc()).limit(8).all())
    result = []
    for row in rows:
        item = db.session.get(Food, row.food_id)
        if item:
            result.append({"id": item.id, "emoji": item.emoji, "name": item.name})
    return jsonify(result)


@app.post("/api/history")
@login_required
def history_add():
    data = request.get_json(silent=True) or {}
    food_id = str(data.get("food_id") or "")[:40]
    if not db.session.get(Food, food_id):
        return jsonify(error="Food not found."), 404
    db.session.add(History(user_id=session["user_id"], food_id=food_id))
    db.session.commit()
    return jsonify(ok=True), 201


if __name__ == "__main__":
    app.run(debug=True)
