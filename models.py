from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    key = db.Column(db.String(30), unique=True, nullable=False)  # lowercase name
    password_hash = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, default=now)


class Food(db.Model):
    """Nutrition values are for one typical serving; `grams` is that serving's weight."""
    __tablename__ = "foods"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    id = db.Column(db.String(40), primary_key=True)
    emoji = db.Column(db.String(8))
    name = db.Column(db.String(80), nullable=False)
    group = db.Column("food_group", db.String(12), default="other")
    diet = db.Column(db.String(2), default="v")  # v = vegetarian, nv = non-veg
    serving = db.Column(db.String(40))
    grams = db.Column(db.Float, default=100)
    kcal = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    fiber = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)
    source = db.Column(db.String(160), default="Demo value (approximate)")

    def to_dict(self):
        return {
            "id": self.id, "emoji": self.emoji, "name": self.name, "group": self.group,
            "diet": self.diet, "serving": self.serving, "grams": self.grams,
            "kcal": self.kcal, "protein": self.protein, "carbs": self.carbs,
            "fat": self.fat, "fiber": self.fiber, "sugar": self.sugar,
            "sodium": self.sodium, "source": self.source,
        }


class History(db.Model):
    __tablename__ = "history"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    food_id = db.Column(db.String(40), db.ForeignKey("foods.id"), nullable=False)
    at = db.Column(db.DateTime, default=now)
