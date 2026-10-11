# Foodify (lite)

Look up foods, scale the portion, compare two foods and build a meal. HTML, CSS and JavaScript in the browser,
Python + Flask on the server, MySQL (or SQLite while learning). One service, one link.

## Run it on your computer
```
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 and register. With no `DATABASE_URL`, it uses a local SQLite file (`instance/foodify.db`).
`requirements.txt` pins SQLAlchemy below 2.1 because some Windows laptops block a compiled file in 2.1.

## Use your filess.io MySQL database
Set `DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME` (values from your dashboard; URL-encode special characters in the password).
Tables and the 48 starter foods are created on first start. The free plan allows few connections, so the app uses a pool of 2.

## Deploy on Render
1. Put this folder on GitHub (`.gitignore` skips `venv`, `instance` and `.env`).
2. Render: New > Web Service > connect the repo.
3. Build command: `pip install -r requirements.txt`   Start command: `gunicorn -w 1 --threads 4 app:app`
4. Environment variables: `DATABASE_URL`, `SECRET_KEY` (long random text), `SESSION_COOKIE_SECURE` = `1`.
Free Render services sleep when idle, so the first visit can take about a minute.

## Files
| File | Job |
|---|---|
| `static/index.html` | The app page: 3 tabs with empty boxes |
| `static/login.html` | Login and register page |
| `static/style.css` | Colours and layout |
| `static/app.js` | Search, portion calculator, compare, meal, history |
| `static/login.js` | Sends login/register to the server |
| `app.py` | Flask: pages, JSON API, login sessions |
| `models.py` | The 3 database tables (users, foods, history) |
| `seed_data.py` | The 48 starter foods |

## How it works
1. The browser asks for `/`. Flask checks the login cookie; no cookie means redirect to `/login.html`.
2. `login.js` posts the name and password to `/api/login` (or `/api/register`). Flask checks the salted hash and stores the user id in a signed cookie.
3. `app.js` loads your name from `/api/me` and all foods from `/api/foods`, then draws the page from that data.
4. Opening a food saves a row in `history`, and the page shows your recent foods.

## API
| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/foods`, `/api/foods?q=dos` | all foods, or a search |
| GET | `/api/foods/<id>` | one food |
| POST | `/api/register`, `/api/login` | JSON `{name, password}` |
| GET | `/logout` | clears the session |
| GET | `/api/me` | needs login |
| GET, POST | `/api/history` | needs login |

## Honest limits
- The 48 food values are approximate demo numbers. Replace them with IFCT 2017 / USDA FoodData Central values before real use.
- No photo recognition yet. That would be a later feature (a trained image model behind a new `/api/recognize` route).
- No password reset, email or admin page. Anyone can register.
- Keep `SECRET_KEY` private and never commit a real database URL.
