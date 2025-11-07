from flask import Flask, render_template, request, url_for, redirect

import os
from werkzeug.utils import secure_filename



app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- PRZYKŁADOWE DANE ---
recipes_data = {
    'sniadanie': [
        {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
                {'id': 1, 'name': 'Jajecznica z pomidorami', 'time': '10 min', 'difficulty': 'Łatwy', 'image': 'jajecznica.jpg', 'rating': 4},
        {'id': 2, 'name': 'Owsianka z owocami', 'time': '5 min', 'difficulty': 'Łatwy', 'image': 'temp.jpg', 'rating': 5},
    ],
    'obiad': [
        {'id': 1, 'name': 'Schabowy z ziemniakami', 'time': '40 min', 'difficulty': 'Średni', 'image': 'schabowy.jpg', 'rating': 4},
        {'id': 2, 'name': 'Spaghetti bolognese', 'time': '30 min', 'difficulty': 'Łatwy', 'image': 'pizza.jpg', 'rating': 5},
    ],
    'deser': []
}

# --- STRONA GŁÓWNA ---
@app.route('/')
def index():
    return render_template('index.html', categories=recipes_data.keys())


# --- LISTA PRZEPISÓW DLA KATEGORII ---
@app.route('/category/<category>')
def category(category):
    recipes = recipes_data.get(category, [])

    # Dodaj dynamiczne linki do przepisów
    for recipe in recipes:
        recipe['url'] = url_for('recipe_detail', recipe_id=recipe['id'])

    # Obsługa wyszukiwania
    query = request.args.get('q', '').lower()
    if query:
        recipes = [r for r in recipes if query in r['name'].lower()]

    return render_template('category.html', category=category, recipes=recipes)


# --- STRONA SZCZEGÓŁÓW PRZEPISU ---
@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    # Na razie 1 przykładowy przepis
    recipe = {
        'id': recipe_id,
        'name': 'Ciasto dyniowe z polewą',
        'image': 'pizza.jpg',
        'difficulty': 'Łatwy',
        'time': '1 godzina',
        'servings': 20,
        'ingredients': [
            '250 g puree z pieczonej dyni',
            '200 g masła',
            '1 szklanka cukru',
            '1 opakowanie cukru wanilinowego',
            'Skórka starta z 1 pomarańczy lub 2 mandarynek',
            '3 jajka (oddzielnie żółtka i białka)',
            '225 g mąki pszennej',
            '1 łyżeczka proszku do pieczenia',
            '1 łyżeczka sody oczyszczonej'
        ],
        'icing': ['50 g białej czekolady lub 5 łyżek cukru pudru'],
        'steps': [
            'Tortownicę o średnicy 23–24 cm posmarować masłem...',
            'Piekarnik nagrzać do 180°C...',
            'Mus z dyni przełożyć do miski...',
            'Białka ubić na sztywną pianę...',
            'Masę przełożyć do tortownicy i piec...',
            'Polewa: do odłożonej masy dodać roztopioną białą czekoladę...'
        ]
    }

    return render_template('recipe.html', recipe=recipe)


# --- FORMULARZ DODAWANIA PRZEPISU ---

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        # dane tekstowe
        name = request.form.get('name')
        category = request.form.get('category')
        time = request.form.get('time')
        difficulty = request.form.get('difficulty')
        portions = request.form.get('portions')
        ingredients = request.form.getlist('ingredients')
        steps = request.form.getlist('steps')

        # plik zdjęcia
        file = request.files.get('image')
        filename = 'placeholder.jpg'

        print("Plik przesłany:", file)
        if file:
            print("Nazwa pliku:", file.filename)



        file = request.files.get('image')
        filename = 'placeholder.jpg'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            print("Plik zapisany:", save_path)
        else:
            print("Nie przesłano pliku lub nieprawidłowe rozszerzenie.")

        # dodanie przepisu
        new_id = len(recipes_data.get(category, [])) + 1
        new_recipe = {
            'id': new_id,
            'name': name,
            'time': time,
            'difficulty': difficulty,
            'image': filename,
            'rating': 0,
            'portions': portions,
            'ingredients': [i for i in ingredients if i.strip()],
            'steps': [s for s in steps if s.strip()]
        }

        recipes_data.setdefault(category, []).append(new_recipe)
        return redirect(url_for('category', category=category))

    return render_template('add_recipe.html', categories=recipes_data.keys())


@app.route('/login.html')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.run(debug=True)
