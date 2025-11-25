from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

ADMIN_USERNAME=os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
ADMIN_EMAIL=os.getenv("ADMIN_EMAIL")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = int(os.getenv("POSTGRES_PORT"))

limiter = Limiter(
    get_remote_address,
    app=app,
    headers_enabled=True
)

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    comments = db.relationship("Comment", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50))
    difficulty = db.Column(db.String(50))
    portions = db.Column(db.String(50))
    image = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0)

    ingredients = db.relationship("Ingredient", backref="recipe", cascade="all, delete-orphan")
    steps = db.relationship("Step", backref="recipe", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe {self.name}>"

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    def __repr__(self):
        return self.text

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    def __repr__(self):
        return f"Krok {self.order}"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    def __repr__(self):
        return f"<Comment {self.id}>"

def calculate_rating(recipe):
    avg_rating = db.session.query(db.func.avg(Comment.rating)).filter_by(recipe_id=recipe.id).scalar()
    recipe.rating = round(avg_rating, 2) if avg_rating else 0
    db.session.commit()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Musisz być zalogowany, aby uzyskać dostęp.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin", False):
            flash("Musisz być administratorem.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/category/<category>")
def category(category):
    q = request.args.get('q', '')
    if q:
        recipes = Recipe.query.filter(
            Recipe.category == category,
            Recipe.name.ilike(f"%{q}%")
        ).all()
    else:
        recipes = Recipe.query.filter_by(category=category).all()
    return render_template("category.html", category=category, recipes=recipes)

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    user_comment = None
    if "username" in session:
        user = User.query.filter_by(username=session["username"]).first()
        if user:
            user_comment = Comment.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
    return render_template("recipe.html", recipe=recipe, user_comment=user_comment)

@limiter.limit("5 per minute")
@app.route("/recipe/<int:recipe_id>/add_comment", methods=["POST"])
@login_required
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    user = User.query.filter_by(username=session["username"]).first()

    existing_comment = Comment.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
    if existing_comment:
        flash("Komentarz już istnieje.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe.id))

    rating = int(request.form.get("rating"))
    text = request.form.get("text").strip()

    if not text or rating < 1 or rating > 5:
        flash("Nieprawidłowe dane komentarza.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe.id))

    comment = Comment(text=text, rating=rating, user=user, recipe=recipe)
    db.session.add(comment)
    db.session.commit()
    calculate_rating(recipe)
    flash("Komentarz dodany!", "success")
    return redirect(url_for("recipe_detail", recipe_id=recipe.id))

@app.route("/recipe/<int:recipe_id>/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(recipe_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    user = User.query.filter_by(username=session["username"]).first()

    if comment.user_id != user.id and not session.get("is_admin"):
        flash("Brak uprawnień.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe_id))

    db.session.delete(comment)
    db.session.commit()
    recipe = Recipe.query.get(recipe_id)
    calculate_rating(recipe)
    flash("Komentarz usunięty.", "success")
    return redirect(url_for("recipe_detail", recipe_id=recipe_id))

@limiter.limit("5 per minute")
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session["username"] = user.username
        session["email"] = user.email
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin
        flash("Zalogowano pomyślnie!", "success")
        if user.is_admin:
            return redirect(url_for("admin_dashboard"))
    else:
        flash("Nieprawidłowe dane logowania", "error")
    return redirect(url_for("index"))

@limiter.limit("5 per minute")
@app.route("/register", methods=["POST"])
def register():
    '''
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    if User.query.filter_by(username=username).first():
        flash("Użytkownik już istnieje!", "error")
        return redirect(url_for("index"))
    new_user = User(username=username, email=email, password=generate_password_hash(password), is_admin=False)
    db.session.add(new_user)
    db.session.commit()
    flash("Zarejestrowano pomyślnie!", "success")
    return redirect(url_for("index"))
    '''
    pass

@app.route("/logout")
def logout():
    session.clear()
    flash("Wylogowano.", "success")
    return redirect(url_for("index"))


@limiter.limit("10 per minute")
@app.route("/admin")
@admin_required
def admin_dashboard():
    recipes = Recipe.query.all()
    users = User.query.all()
    comments = Comment.query.all()
    return render_template("admin_dashboard.html", 
                         recipes=recipes, 
                         users=users, 
                         comments=comments)

@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == session.get("user_id"):
        flash("Nie możesz usunąć samego siebie!", "error")
        return redirect(url_for("admin_dashboard"))
    
    db.session.delete(user)
    db.session.commit()
    flash(f"Użytkownik {user.username} i jego komentarze zostały usunięte.", "success")
    return redirect(url_for("admin_dashboard"))


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@limiter.limit("25 per minute")
@app.route("/admin/recipe/add", methods=["GET", "POST"])
@admin_required
def add_recipe():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        time = request.form.get("time")
        difficulty = request.form.get("difficulty")
        portions = request.form.get("portions")
        image_file = request.files.get("image")

        filename = "placeholder.jpg"
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)

        new_recipe = Recipe(
            name=name,
            category=category,
            time=time,
            difficulty=difficulty,
            portions=portions,
            image=filename
        )
        db.session.add(new_recipe)
        db.session.commit()

        ingredients = request.form.getlist("ingredients")
        for text in ingredients:
            if text.strip():
                db.session.add(Ingredient(text=text.strip(), recipe=new_recipe))

        steps = request.form.getlist("steps")
        for order, text in enumerate(steps, start=1):
            if text.strip():
                db.session.add(Step(text=text.strip(), order=order, recipe=new_recipe))

        db.session.commit()
        flash("Przepis dodany pomyślnie!", "success")
        return redirect(url_for("admin_dashboard"))

    CATEGORIES = ["obiad", "śniadanie", "kolacja"]
    return render_template('add_recipe.html', categories=CATEGORIES)

@app.route("/admin/recipe/<int:recipe_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == "POST":
        recipe.name = request.form.get("name")
        recipe.category = request.form.get("category")
        recipe.time = request.form.get("time")
        recipe.difficulty = request.form.get("difficulty")
        recipe.portions = request.form.get("portions")
        recipe.image = request.form.get("image")
        db.session.commit()
        flash("Przepis zaktualizowany!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit_recipe.html", recipe=recipe)

@app.route("/admin/recipe/<int:recipe_id>/delete", methods=["POST"])
@admin_required
def admin_delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    flash("Przepis usunięty!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/recipe/<int:recipe_id>/ingredients")
@admin_required
def admin_recipe_ingredients(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template("admin_ingredients.html", recipe=recipe)

@app.route("/admin/recipe/<int:recipe_id>/ingredient/add", methods=["POST"])
@admin_required
def admin_add_ingredient(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    text = request.form.get("text")
    if text:
        ingredient = Ingredient(text=text, recipe_id=recipe.id)
        db.session.add(ingredient)
        db.session.commit()
        flash("Składnik dodany!", "success")
    return redirect(url_for("admin_recipe_ingredients", recipe_id=recipe_id))

@app.route("/admin/ingredient/<int:ingredient_id>/delete", methods=["POST"])
@admin_required
def admin_delete_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    recipe_id = ingredient.recipe_id
    db.session.delete(ingredient)
    db.session.commit()
    flash("Składnik usunięty!", "success")
    return redirect(url_for("admin_recipe_ingredients", recipe_id=recipe_id))

@app.route("/admin/recipe/<int:recipe_id>/steps")
@admin_required
def admin_recipe_steps(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template("admin_steps.html", recipe=recipe)

@app.route("/profile/delete", methods=["POST"])
@login_required
def delete_my_account():
    user = User.query.get_or_404(session["user_id"])
    
    db.session.delete(user)
    db.session.commit()
    
    session.clear()
    
    flash("Twoje konto zostało trwale usunięte. Dane zniknęły z bazy.", "success")
    return redirect(url_for("index"))


@app.route("/admin/recipe/<int:recipe_id>/step/add", methods=["POST"])
@admin_required
def admin_add_step(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    text = request.form.get("text")
    order = request.form.get("order", type=int)
    if text and order:
        step = Step(text=text, order=order, recipe_id=recipe.id)
        db.session.add(step)
        db.session.commit()
        flash("Krok dodany!", "success")
    return redirect(url_for("admin_recipe_steps", recipe_id=recipe_id))

@app.route("/admin/step/<int:step_id>/delete", methods=["POST"])
@admin_required
def admin_delete_step(step_id):
    step = Step.query.get_or_404(step_id)
    recipe_id = step.recipe_id
    db.session.delete(step)
    db.session.commit()
    flash("Krok usunięty!", "success")
    return redirect(url_for("admin_recipe_steps", recipe_id=recipe_id))

@app.route("/admin/comment/<int:comment_id>/delete", methods=["POST"])
@admin_required
def admin_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    recipe_id = comment.recipe_id
    db.session.delete(comment)
    db.session.commit()
    recipe = Recipe.query.get(recipe_id)
    calculate_rating(recipe)
    flash("Komentarz usunięty!", "success")
    return redirect(url_for("admin_dashboard"))

def init_db():
    with app.app_context():
        db.create_all()
        
        if ADMIN_USERNAME and ADMIN_PASSWORD:
            if not User.query.filter_by(username=ADMIN_USERNAME).first():
                admin_user = User(
                    username=ADMIN_USERNAME,
                    password=generate_password_hash(ADMIN_PASSWORD),
                    email=ADMIN_EMAIL,
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("--- BAZA ZAINICJOWANA, ADMIN UTWORZONY ---")


init_db()

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.run()
