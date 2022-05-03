from flask import Flask, render_template, redirect, flash, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

added_ingredients = {}

def check_form(form):
    if len(form) < 2:
        print("too short")
        return False
    elif len(form) > 40:
        print("too long")
        return False
    return True

def check_user():
    if session.get("username"):
        print("access granted")
        return True
    print("access denied, not logged in")
    return False

@app.route("/")
def index():
    sql = db.session.execute("SELECT name FROM recipes")
    recipes = sql.fetchall()
    return render_template("index.html", recipes=recipes)

@app.route("/newcocktail", methods=["GET","POST"])
def newcocktail():
    if not check_user():
        return redirect("/") #todo ilmoita virheestä
    sql0 = db.session.execute("SELECT name FROM ingredient WHERE is_alc = TRUE ORDER BY name ASC")
    alcohols = sql0.fetchall()
    sql1 = db.session.execute("SELECT name FROM ingredient WHERE is_alc = FALSE ORDER BY name ASC")
    mixers = sql1.fetchall()
    return render_template("newcocktail.html", alcohols=alcohols, mixers=mixers, ingredients=added_ingredients)

@app.route("/newcocktail2", methods=["GET","POST"])
def newcocktail2():
    if not check_user():
        return redirect("/") #todo ilmoita virheestä
    if len(added_ingredients) == 0:
        return redirect("newcocktail")
    return render_template("newcocktail2.html", ingredients=added_ingredients)

@app.route("/makecocktail", methods=["GET","POST"])
def makecocktail():
    name = request.form["name"]
    desc = request.form["description"]
    sql0 = "INSERT INTO recipes (name,description) VALUES (:name,:description) RETURNING id"
    result = db.session.execute(sql0, {"name":name, "description":desc})
    rec_id = result.fetchone()
    
    sql2 = "INSERT INTO recipe_ingredient (ingredient_id, recipe_id, amount) VALUES (:ing_id,:rec_id,:amount)"
    for ingredient in added_ingredients:
        print(ingredient)
        sql1 = "SELECT id FROM ingredient WHERE name = (:name)"
        sql1ex = db.session.execute(sql1, {"name":ingredient})
        ing_id = sql1ex.fetchone()
        amount = added_ingredients[ingredient]
        db.session.execute(sql2,{"ing_id":ing_id.id,"rec_id":rec_id.id,"amount":amount})
    db.session.commit()
    return redirect("/")     

@app.route("/cocktail/<cocktailname>")
def cocktail(cocktailname):
    session["current_cocktail"] = cocktailname
    sql0 = "SELECT id FROM recipes WHERE name= (:cocktailname)"
    sqlex0 = db.session.execute(sql0, {"cocktailname":cocktailname})
    idresult = sqlex0.fetchone()
    id = idresult[0]
    session["recipe_id"] = id
    
    sql1 = "SELECT ingredient.name, recipe_ingredient.amount FROM ingredient RIGHT JOIN recipe_ingredient ON recipe_ingredient.ingredient_id=ingredient.id AND recipe_ingredient.recipe_id= (:id) WHERE ingredient.name IS NOT NULL;"
    sqlex1 = db.session.execute(sql1, {"id":id})
    ingredients = sqlex1.fetchall()
    
    sql2 = "SELECT description FROM recipes WHERE name =(:cocktailname)"
    sqlex2 = db.session.execute(sql2, {"cocktailname":cocktailname})
    desc = sqlex2.fetchone()
    
    sql3 = "SELECT users.name, reviews.content, reviews.rating, DATE(reviews.sent_at) FROM reviews RIGHT JOIN users ON reviews.user_id=users.id AND reviews.recipe_id= (:id) WHERE reviews.content IS NOT NULL"
    sqlex3 = db.session.execute(sql3, {"id":id})
    reviews = sqlex3.fetchall()
    
    return render_template("cocktail.html", cocktailname=cocktailname, ingredients=ingredients, description=desc, reviews=reviews)

@app.route("/leave_review", methods=["POST", "GET"])
def leave_review():
    cocktailname = session.get("current_cocktail")
    content = request.form["review_text"]
    user_id = session.get("user_id")
    recipe_id = session.get("recipe_id")
    rating = request.form["review_rating"]
    sql = "INSERT INTO reviews (content, user_id, recipe_id, rating, sent_at) VALUES (:content, :user_id, :recipe_id, :rating, :sent_at)"
    db.session.execute(sql, {"content":content,"user_id":user_id,"recipe_id":recipe_id,"rating":rating})
    db.session.commit()
    return redirect("/cocktail/" + cocktailname)
    
@app.route("/addmixer", methods=["POST", "GET"])
def addmixer():
    mixer = request.form["mixer"]
    amount = int(request.form["amount"])
    added_ingredients[mixer]=amount
    return redirect(url_for("newcocktail", ingredients=added_ingredients))

@app.route("/addalcohol", methods=["POST", "GET"])
def addalcohol():
    alcohol = request.form["alcohol"]
    amount = int(request.form["amount"])
    added_ingredients[alcohol]=amount
    return redirect(url_for("newcocktail", ingredients=added_ingredients))

@app.route("/reset", methods=["POST","GET"])
def reset():
    added_ingredients.clear()
    return redirect(url_for("newcocktail", ingredients=added_ingredients))

@app.route("/addingredient")
def addingredient():
    if not check_user():
        return redirect("/") #todo ilmoita virheestä
    return render_template("addingredient.html")

@app.route("/newingredient", methods=["POST"])
def newingredient():
    name = request.form["name"]
    is_alc = request.form["is_alc"]
    sql = "INSERT INTO ingredient (name,is_alc) VALUES (:name,:is_alc)"
    db.session.execute(sql,{"name":name,"is_alc":is_alc})
    db.session.commit()
    return redirect("/newcocktail")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/createuser", methods=["POST"])
def createuser():
    sql = "INSERT INTO users (name,password,is_admin) VALUES (:name,:password,FALSE)"
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if check_form(username) and check_form(password1):
        print("checks passed")
        if password1 == password2:
            password = generate_password_hash(password1)
            db.session.execute(sql,{"name":username,"password":password})
            db.session.commit()
            print("käyttäjä luotu!")
            return redirect("/")
        else:
            print("salasanat eivät täsmää")
            return redirect("/newuser")
    else:
        return redirect("/newuser")

@app.route("/login", methods=["POST"])
def login():
    print("loggataa inee")
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT id, password FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        print("Väärä käyttäjänimi")
        return redirect("/userlogin") #todo ilmoita että väärä käyttäjä
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            print("username and password correct")
            session["username"] = username
            session["user_id"] = user[0]
        else:
            print("Väärä salasana")
            return redirect("/userlogin") #todo ilmoita että väärä salasana
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")