import os
import json
import random
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import app, db, Recipe, Ingredient, Step, User, Comment, calculate_rating

load_dotenv()

RECIPES_DIR = os.path.join(os.path.dirname(__file__), "recipes")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD")

TEST_USERNAMES = [
    "Arkadiusz Abacki", "Monika Babacka", "Tomasz Cabacki", "Klaudia Dabacka", "Mirosław Ebacki"
]

TEST_COMMENTS = [
    {"text": "Świetny przepis, bardzo smaczne!", "rating": 5},
    {"text": "Na pewno zrobię ponownie.", "rating": 4},
    {"text": "Trochę za słone, ale okej.", "rating": 3},
    {"text": "Uwielbiam to danie.", "rating": 5},
    {"text": "Wyszło idealnie!", "rating": 5},
    {"text": "Proste i szybkie do zrobienia.", "rating": 4},
    {"text": "Moim dzieciom bardzo smakowało.", "rating": 5},
    {"text": "Wprowadziłem kilka zmian i dalej super.", "rating": 4},
    {"text": "Robię już trzeci raz!", "rating": 5},
    {"text": "Zbyt skomplikowane kroki.", "rating": 2},
    {"text": "Smak mega!", "rating": 5},
    {"text": "Fajna propozycja na obiad.", "rating": 4},
    {"text": "Nie wyszło mi, ale spróbuję ponownie.", "rating": 3},
    {"text": "Dobre, ale następnym razem dam mniej przypraw.", "rating": 4},
    {"text": "Bardzo dobre proporcje.", "rating": 5},
    {"text": "Polecam każdemu.", "rating": 5},
    {"text": "Wyjątkowo udane danie.", "rating": 5},
    {"text": "Szybkie w przygotowaniu.", "rating": 4},
    {"text": "Zrobię to na rodzinne spotkanie.", "rating": 5},
    {"text": "Moje ulubione!", "rating": 5},
]

def create_test_users():
    users = []
    for username in TEST_USERNAMES:
        email = f"{username}@example.com"

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(TEST_USER_PASSWORD)
            )
            db.session.add(user)
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")
        users.append(user)

    db.session.commit()
    return users

def generate_comments(users):
    recipes = Recipe.query.all()

    for recipe in recipes:
        num_comments = random.randint(2,5)

        comments_for_recipe = random.sample(TEST_COMMENTS, num_comments)
        users_for_recipe = random.sample(users, num_comments)

        for comment_data, user in zip(comments_for_recipe, users_for_recipe):
            if Comment.query.filter_by(recipe_id=recipe.id, user_id=user.id).first():
                continue

            new_comment = Comment(
                text=comment_data["text"],
                rating=comment_data["rating"],
                recipe_id=recipe.id,
                user_id=user.id
            )
            db.session.add(new_comment)
            print(f"Added comment by {user.username} to recipe {recipe.name}")

        db.session.commit()
        calculate_rating(recipe)

def read_recipe(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if Recipe.query.filter_by(name=data["name"]).first():
        return

    new_recipe = Recipe(
        name=data["name"],
        category=data.get("category", "obiad"),
        time=data.get("time", 30),
        difficulty=data.get("difficulty", "Średni"),
        portions=data.get("portions", 2),
        image=data.get("image_filename", "placeholder.jpg")
    )
    db.session.add(new_recipe)
    db.session.commit()

    for ingredient in data.get("ingredients", []):
        new_ingredient = Ingredient(text=ingredient, recipe=new_recipe)
        db.session.add(new_ingredient)

    for step in data.get("steps", []):
        new_step = Step(text=step, recipe=new_recipe)
        db.session.add(new_step)

    db.session.commit()

def import_recipes():
    for filename in os.listdir(RECIPES_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(RECIPES_DIR, filename)
            read_recipe(file_path)
    print("Recipes loaded into database!")

if __name__ == "__main__":
    with app.app_context():
        import_recipes()
        users = create_test_users()
        generate_comments(users)
        print("Database populated successfully!")
