from app import app
from flask import render_template, redirect, flash, request, session, url_for
import users, cocktail

def check_form(form):
    if len(form) <= 2:
        return False
    if len(form) > 40:
        return False
    return True

def check_user():
    if session.get("username"):
        return True
    return False

@app.route("/")
def index():
    recipes = cocktail.get_cocktails()
    return render_template("index.html", recipes=recipes)

@app.route("/newcocktail", methods=["GET","POST"])
def newcocktail():
    list = cocktail.get_added_ingredients()
    if not check_user():
        flash("Sinun tulee olla kirjautuneena sisään tehdäksesi cocktailin.")
        return redirect("/") 
    ingredients = cocktail.get_ingredient_list()
    return render_template("newcocktail.html", alcohols=ingredients[0], mixers=ingredients[1], ingredients=list)

@app.route("/newcocktail2", methods=["GET","POST"])
def newcocktail2():
    list = cocktail.get_added_ingredients()
    if not check_user():
        return redirect("/") #todo ilmoita virheestä
    if len(list) == 0:
        return redirect("newcocktail")
    return render_template("newcocktail2.html", ingredients=list)

@app.route("/makecocktail", methods=["GET","POST"])
def makecocktail():
    list = cocktail.get_added_ingredients()
    if request.method == "GET":
        return render_template("newcocktail2.html", ingredients=list)
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["description"]
        if cocktail.makecocktail(name,desc):
            return redirect("/")
        else:
            return redirect("/newcocktail2")

@app.route("/cocktail/<cocktailname>")
def cocktail_info(cocktailname):
    session["current_cocktail"] = cocktailname
    info = cocktail.get_cocktail_info(cocktailname)
    return render_template("cocktail.html", cocktailname=cocktailname, ingredients=info[0], description=info[1], reviews=info[2])

@app.route("/leave_review", methods=["POST", "GET"])
def leave_review():
    cocktailname = session.get("current_cocktail")
    if request.method == "GET":
        return redirect("/cocktail/" + cocktailname)
    if request.method == "POST":
        content = request.form["review_text"]
        rating = request.form["review_rating"]
        if check_form(content):
            if cocktail.leave_review(content, rating):
                return redirect("/cocktail/" + cocktailname)
            else:
                return redirect("/cocktail/" + cocktailname)
    return redirect("/cocktail/" + cocktailname) #todo ilmoita virheestä
    
@app.route("/addmixer", methods=["POST", "GET"])
def addmixer():
    mixer = request.form["mixer"]
    amount = int(request.form["amount"])
    cocktail.addmixer(mixer, amount)
    list = cocktail.get_added_ingredients()
    return redirect(url_for("newcocktail", ingredients=list))

@app.route("/addalcohol", methods=["POST", "GET"])
def addalcohol():
    alcohol = request.form["alcohol"]
    amount = int(request.form["amount"])
    cocktail.addalcohol(alcohol, amount)
    list = cocktail.get_added_ingredients()
    return redirect(url_for("newcocktail", ingredients=list))

@app.route("/reset", methods=["POST","GET"])
def reset():
    cocktail.reset()
    list = cocktail.get_added_ingredients()
    return redirect(url_for("newcocktail", ingredients=list))

@app.route("/addingredient")
def addingredient():
    if not check_user():
        return redirect("/") #todo ilmoita virheestä
    return render_template("addingredient.html")

@app.route("/newingredient", methods=["POST"])
def newingredient():
    name = request.form["name"]
    is_alc = request.form["is_alc"]
    if cocktail.newingredient(name, is_alc):
        return redirect("/newcocktail")
    else:
        return redirect("/newcocktail") #todo ilmoita virheestä

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/createuser", methods=["POST", "GET"])
def createuser():
    if request.method == "GET":
        return render_template("newuser.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if check_form(username) and check_form(password1):
            print("checks passed")
            if password1 == password2:
                if users.createuser(username, password1):
                    print("käyttäjä luotu!")
                    return redirect("/")
            else:
                print("salasanat eivät täsmää")
                return redirect("/newuser")
    return render_template("newuser.html") #todo ilmoita virheestä

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("userlogin.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("userlogin.html")
        
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/result", methods=["GET"])
def result():
    query = request.args["query"]
    if check_form(query):
        if not cocktail.search(query):
            error = "Valitettavasti haku ei tuottanut tulosta :(. Kirjoitithan hakusanan oikein?"
            return render_template("result.html", error=error, query=query)
        else:
            results = cocktail.search(query)
            return render_template("result.html", results=results, query=query)
    return redirect("/")