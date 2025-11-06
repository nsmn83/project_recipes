from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/category.html')
def category():
    return render_template('category.html')

@app.route('/recipe.html')
def recipe():
    return render_template('recipe.html')

if __name__ == '__main__':
    app.run(debug=True)
