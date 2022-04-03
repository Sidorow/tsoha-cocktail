from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)


@app.route("/")
def index():
    sql = db.session.execute("SELECT name FROM recipes")
    recipes = sql.fetchall()
    return render_template("index.html", recipes=recipes)

@app.route("/newcocktail")
def page1():
    result = db.session.execute("SELECT name FROM ingredients")
    ingredients = result.fetchall()
    return render_template("newcocktail.html", ingredients=ingredients)

@app.route("/cocktail/<cocktailname>")
def cocktail(cocktailname):
    sql = "SELECT ingredients FROM recipes WHERE name = (:cocktailname)"
    sqlex = db.session.execute(sql, {"cocktailname":cocktailname})
    ingredients = sqlex.fetchone()
    #ingredients = result.split(",")
    return render_template("cocktail.html", cocktailname=cocktailname, ingredients=ingredients)