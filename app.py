from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 📦 Konfiguracja bazy danych (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 📁 Upload folder
CATEGORIES = ['sniadanie', 'obiad', 'kolacja', 'deser']
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# --- MODELE ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")

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

    ingredients = db.relationship("Ingredient", back_populates="recipe", cascade="all, delete")
    steps = db.relationship("Step", back_populates="recipe", cascade="all, delete")
    comments = db.relationship("Comment", back_populates="recipe", cascade="all, delete")

    def __repr__(self):
        return f"<Recipe {self.name}>"


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    recipe = db.relationship("Recipe", back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient {self.text[:30]}>"


class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    recipe = db.relationship("Recipe", back_populates="steps")

    def __repr__(self):
        return f"<Step {self.order}: {self.text[:30]}>"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)

    user = db.relationship("User", back_populates="comments")
    recipe = db.relationship("Recipe", back_populates="comments")

    def __repr__(self):
        return f"<Comment by {self.user.username} on {self.recipe.name}>"


# --- Pomocnicze funkcje ---

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Dekoratory ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Musisz być zalogowany, aby uzyskać dostęp.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Brak uprawnień administratora.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# --- ROUTES ---

@app.route("/")
def index():
    categories = db.session.query(Recipe.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template("index.html", categories=categories)


@app.route("/category/<category>")
def category(category):
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




@app.route("/add_recipe", methods=["GET", "POST"])
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

        # dodaj składniki
        ingredients = request.form.getlist("ingredients")
        for text in ingredients:
            if text.strip():
                db.session.add(Ingredient(text=text.strip(), recipe=new_recipe))

        # dodaj kroki
        steps = request.form.getlist("steps")
        for order, text in enumerate(steps, start=1):
            if text.strip():
                db.session.add(Step(text=text.strip(), order=order, recipe=new_recipe))

        db.session.commit()
        flash("Przepis dodany pomyślnie!", "success")
        return redirect(url_for("category", category=category))

    return render_template('add_recipe.html', categories=CATEGORIES)


@app.route("/recipe/<int:recipe_id>/add_comment", methods=["POST"])
@login_required
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    user = User.query.filter_by(username=session["username"]).first()

    # Sprawdź, czy użytkownik już dodał komentarz do tego przepisu
    existing_comment = Comment.query.filter_by(recipe_id=recipe.id, user_id=user.id).first()
    if existing_comment:
        flash("Komentarz już istnieje. Możesz go edytować lub usunąć.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe.id))

    # Pobierz dane z formularza
    rating = int(request.form.get("rating"))
    text = request.form.get("text").strip()

    if not text or rating < 1 or rating > 5:
        flash("Nieprawidłowe dane komentarza.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe.id))

    comment = Comment(text=text, rating=rating, user=user, recipe=recipe)
    db.session.add(comment)
    db.session.commit()

    # Aktualizuj średnią ocenę przepisu
    avg_rating = db.session.query(db.func.avg(Comment.rating)).filter_by(recipe_id=recipe.id).scalar()
    recipe.rating = round(avg_rating, 2)
    db.session.commit()

    flash("Komentarz dodany!", "success")
    return redirect(url_for("recipe_detail", recipe_id=recipe.id))


@app.route("/recipe/<int:recipe_id>/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(recipe_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    user = User.query.filter_by(username=session["username"]).first()

    if comment.user_id != user.id:
        flash("Nie możesz usunąć komentarza innego użytkownika.", "error")
        return redirect(url_for("recipe_detail", recipe_id=recipe_id))

    db.session.delete(comment)
    db.session.commit()

    # Aktualizuj średnią ocenę przepisu
    recipe = Recipe.query.get(recipe_id)
    avg_rating = db.session.query(db.func.avg(Comment.rating)).filter_by(recipe_id=recipe.id).scalar()
    recipe.rating = round(avg_rating, 2) if avg_rating else 0
    db.session.commit()

    flash("Komentarz usunięty.", "success")
    return redirect(url_for("recipe_detail", recipe_id=recipe_id))


# --- AUTORYZACJA ---

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session["username"] = user.username
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin
        flash("Zalogowano pomyślnie!", "success")
    else:
        flash("Nieprawidłowe dane logowania", "error")
    return redirect(url_for("index"))


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if User.query.filter_by(username=username).first():
        flash("Użytkownik już istnieje!", "error")
        return redirect(url_for("index"))

    new_user = User(username=username, password=generate_password_hash(password), is_admin=False)
    db.session.add(new_user)
    db.session.commit()

    flash("Zarejestrowano pomyślnie! Zaloguj się.", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Wylogowano.", "success")
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    users = User.query.all()
    recipes = Recipe.query.all()
    comments = Comment.query.all()
    return render_template("admin.html", users=users, recipes=recipes, comments=comments)

# Usuń użytkownika
@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Nie można usunąć administratora!", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"Użytkownik {user.username} został usunięty.", "success")
    return redirect(url_for("admin_dashboard"))

# Usuń komentarz
@app.route("/admin/delete_comment/<int:comment_id>", methods=["POST"])
@admin_required
def admin_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("Komentarz został usunięty.", "success")
    return redirect(url_for("admin_dashboard"))

# Usuń przepis
@app.route("/admin/delete_recipe/<int:recipe_id>", methods=["POST"])
@admin_required
def admin_delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    flash("Przepis został usunięty.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()

        # 🔹 Automatyczne tworzenie konta administratora, jeśli nie istnieje
        if not User.query.filter_by(username="admin").first():
            admin_user = User(
                username="admin",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Konto administratora utworzone: login=admin, hasło=admin123")

    app.run(debug=True)
