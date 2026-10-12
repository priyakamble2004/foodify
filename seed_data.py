from models import Food, db

# id, emoji, name, group, diet, serving, grams, kcal, protein, carbs, fat, fiber, sugar, sodium (mg)
# DEMO VALUES per typical serving. Replace with IFCT 2017 / USDA FoodData Central values before sharing.
FOODS = [
    ("apple", "🍎", "Apple", "fruit", "v", "1 medium", 182, 95, 0.5, 25, 0.3, 4, 19, 2),
    ("banana", "🍌", "Banana", "fruit", "v", "1 medium", 118, 105, 1.3, 27, 0.4, 3, 14, 1),
    ("orange", "🍊", "Orange", "fruit", "v", "1 medium", 130, 62, 1.2, 15, 0.2, 3, 12, 0),
    ("mango", "🥭", "Mango", "fruit", "v", "1 cup sliced", 165, 99, 1.4, 25, 0.6, 2.6, 23, 2),
    ("watermelon", "🍉", "Watermelon", "fruit", "v", "1 cup", 150, 45, 0.9, 11, 0.2, 0.6, 9, 2),
    ("grapes", "🍇", "Grapes", "fruit", "v", "1 cup", 150, 104, 1.1, 27, 0.2, 1.4, 23, 3),
    ("veg", "🥦", "Mixed vegetables", "veg", "v", "1 cup cooked", 150, 55, 3, 11, 0.5, 4, 4, 40),
    ("spinach", "🥬", "Spinach (palak)", "veg", "v", "1 cup cooked", 180, 41, 5.3, 6.8, 0.5, 4.3, 0.8, 126),
    ("carrot", "🥕", "Carrot", "veg", "v", "1 medium", 60, 25, 0.6, 5.8, 0.1, 1.7, 2.9, 42),
    ("tomato", "🍅", "Tomato", "veg", "v", "1 medium", 120, 22, 1.1, 4.8, 0.2, 1.5, 3.2, 6),
    ("cucumber", "🥒", "Cucumber", "veg", "v", "1 cup sliced", 100, 15, 0.7, 3.6, 0.1, 0.5, 1.7, 2),
    ("potato", "🥔", "Boiled potato", "veg", "v", "1 medium", 150, 130, 2.8, 30, 0.2, 3.3, 1.5, 8),
    ("corn", "🌽", "Boiled corn", "veg", "v", "1 cob", 100, 96, 3.4, 21, 1.5, 2.4, 4.5, 15),
    ("rice", "🍚", "Rice", "grain", "v", "1 cup cooked", 158, 205, 4, 45, 0.4, 0.6, 0, 2),
    ("brownrice", "🍚", "Brown rice", "grain", "v", "1 cup cooked", 195, 216, 5, 45, 1.8, 3.5, 0.7, 10),
    ("roti", "🫓", "Roti", "grain", "v", "1 medium", 40, 120, 3.5, 20, 3, 3, 0.5, 120),
    ("paratha", "🫓", "Plain paratha", "grain", "v", "1 medium", 60, 190, 4, 27, 8, 2.5, 0.5, 200),
    ("oats", "🥣", "Oats porridge", "grain", "v", "1 bowl cooked", 234, 166, 5.9, 28, 3.6, 4, 1, 9),
    ("poha", "🍛", "Poha", "grain", "v", "1 plate", 150, 180, 3.5, 32, 4, 2, 2, 250),
    ("idli", "🍘", "Idli", "grain", "v", "2 pieces", 80, 120, 4, 24, 0.5, 1.5, 0.5, 180),
    ("dosa", "🥞", "Plain dosa", "grain", "v", "1 medium", 90, 135, 3.5, 24, 2.8, 1, 0.5, 190),
    ("bread", "🍞", "Whole wheat bread", "grain", "v", "1 slice", 28, 70, 3.6, 12, 1, 1.9, 1.4, 130),
    ("makhana", "🍿", "Roasted makhana", "grain", "v", "30 g", 30, 110, 3, 23, 0.5, 3, 0.3, 5),
    ("dal", "🍲", "Dal", "protein", "v", "1 bowl", 150, 180, 10, 28, 3, 7, 2, 300),
    ("rajma", "🫘", "Rajma curry", "protein", "v", "1 bowl", 150, 200, 12, 30, 3.5, 9, 3, 320),
    ("chana", "🫘", "Boiled chana", "protein", "v", "1 cup", 164, 269, 14.5, 45, 4.2, 12.5, 8, 11),
    ("sprouts", "🌱", "Moong sprouts", "protein", "v", "1 cup", 104, 31, 3.2, 6, 0.2, 1.9, 4.3, 6),
    ("egg", "🥚", "Boiled egg", "protein", "nv", "1 large", 50, 78, 6, 0.6, 5, 0, 0.6, 62),
    ("chicken", "🍗", "Grilled chicken", "protein", "nv", "100 g", 100, 165, 31, 0, 3.6, 0, 0, 74),
    ("fish", "🐟", "Grilled fish", "protein", "nv", "100 g", 100, 110, 22, 0, 2, 0, 0, 80),
    ("almond", "🥜", "Almonds", "protein", "v", "30 g", 30, 170, 6, 6, 15, 3.5, 1.2, 0),
    ("peanuts", "🥜", "Peanuts", "protein", "v", "30 g", 30, 170, 7.7, 4.7, 14.7, 2.6, 1.2, 5),
    ("curd", "🥛", "Curd", "dairy", "v", "1 bowl", 100, 60, 3.5, 5, 3, 0, 5, 45),
    ("milk", "🥛", "Milk (full cream)", "dairy", "v", "1 glass (240 ml)", 244, 149, 8, 12, 8, 0, 12, 105),
    ("paneer", "🧀", "Paneer", "dairy", "v", "50 g", 50, 140, 9, 1.5, 11, 0, 1, 20),
    ("chaas", "🥛", "Buttermilk (chaas)", "dairy", "v", "1 glass (240 ml)", 240, 45, 2.5, 4, 1.5, 0, 4, 250),
    ("chips", "🥔", "Potato chips", "other", "v", "30 g pack", 30, 160, 2, 15, 10, 1, 0.3, 170),
    ("fries", "🍟", "French fries", "other", "v", "medium portion", 117, 365, 4, 48, 17, 4, 0, 250),
    ("samosa", "🥟", "Samosa", "other", "v", "1 piece", 80, 210, 3.5, 22, 12, 2, 1.5, 300),
    ("burger", "🍔", "Burger", "other", "nv", "1 regular", 200, 350, 17, 30, 17, 1, 6, 700),
    ("pizza", "🍕", "Pizza slice", "other", "v", "1 slice", 107, 285, 12, 36, 10, 2, 4, 640),
    ("cola", "🥤", "Cola", "other", "v", "330 ml", 330, 140, 0, 35, 0, 0, 35, 15),
    ("gulab", "🍡", "Gulab jamun", "other", "v", "1 piece", 40, 150, 2, 22, 6, 0, 18, 25),
    ("jalebi", "🍥", "Jalebi", "other", "v", "50 g", 50, 220, 1.5, 35, 8, 0, 25, 15),
    ("icecream", "🍦", "Ice cream", "other", "v", "1 scoop", 66, 137, 2.3, 16, 7.3, 0.5, 14, 53),
    ("chocolate", "🍫", "Milk chocolate", "other", "v", "1 small bar", 40, 214, 3.1, 23.6, 12, 1.4, 21, 24),
    ("noodles", "🍜", "Instant noodles", "other", "v", "1 packet (85 g, before cooking)", 85, 330, 7, 50, 12, 2, 2, 1100),
    ("biryani", "🍛", "Chicken biryani", "other", "nv", "1 plate", 250, 430, 20, 52, 15, 2, 2, 800),
]


def load_seed():
    """Add any foods that are not in the database yet. Safe to run many times."""
    added = 0
    for row in FOODS:
        if db.session.get(Food, row[0]):
            continue
        db.session.add(Food(
            id=row[0], emoji=row[1], name=row[2], group=row[3], diet=row[4], serving=row[5],
            grams=row[6], kcal=row[7], protein=row[8], carbs=row[9], fat=row[10],
            fiber=row[11], sugar=row[12], sodium=row[13],
        ))
        added += 1
    db.session.commit()
    return added