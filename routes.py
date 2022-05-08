from app import app
from flask import abort, render_template, redirect, flash, request, session
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
    cocktail.reset()
    recipes = cocktail.get_cocktails()
    return render_template("index.html", recipes=recipes)

@app.route("/newcocktail", methods=["GET","POST"])
def newcocktail():
    if not check_user():
        flash("Sinun tulee olla kirjautuneena sisään tehdäksesi cocktailin.", "error")
        return redirect("/")
    ingredients = cocktail.get_added_ingredients() #session.get("added_ingredients")
    alc_mix = cocktail.get_ingredient_list()
    return render_template("newcocktail.html", alcohols=alc_mix[0], mixers=alc_mix[1], ingredients=ingredients)

@app.route("/newcocktail2", methods=["GET","POST"])
def newcocktail2():
    if not check_user():
        return redirect("/")
    list = cocktail.get_added_ingredients()
    if len(list) == 0:
        return redirect("/newcocktail")
    return render_template("newcocktail2.html", ingredients=list)

@app.route("/makecocktail", methods=["GET","POST"])
def makecocktail():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    list = session.get("added_ingredients") #cocktail.get_added_ingredients()
    if request.method == "GET":
        return render_template("newcocktail2.html", ingredients=list)
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["description"]
        if cocktail.makecocktail(name,desc):
            flash("Cocktaili luotu onnistuneesti!", "message")
            return redirect("/")
        else:
            flash("Jotain meni pieleen. Varmista että cocktailillasi on uniikki nimi!", "error")
            return redirect("/newcocktail2")

@app.route("/cocktail/<cocktailname>")
def cocktail_info(cocktailname):
    session["current_cocktail"] = cocktailname
    info = cocktail.get_cocktail_info(cocktailname)
    return render_template("cocktail.html", cocktailname=cocktailname, ingredients=info[0], description=info[1], reviews=info[2])

@app.route("/leave_review", methods=["POST", "GET"])
def leave_review():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    cocktailname = session.get("current_cocktail")
    if not check_user():
        return redirect("/cocktail" + cocktailname)
    if request.method == "GET":
        return redirect("/cocktail/" + cocktailname)
    if request.method == "POST":
        content = request.form["review_text"]
        rating = request.form["review_rating"]
        if check_form(content):
            if cocktail.leave_review(content, rating):
                return redirect("/cocktail/" + cocktailname)
            else:
                flash("Hups! jotain meni pieleen :(", "error")
                return redirect("/cocktail/" + cocktailname)
    flash("Et voi jättää tekstikenttää tyhjäksi!", "error")
    return redirect("/cocktail/" + cocktailname)
    
@app.route("/addmixer", methods=["POST"])
def addmixer():
    if request.method == "POST":
        mixer = request.form["mixer"]
        if request.form["amount"]:
            amount = int(request.form["amount"])
        else:
            amount = 1
        if cocktail.addmixer(mixer, amount):
            session["added_ingredients"] = cocktail.addmixer(mixer, amount)
            return redirect("/newcocktail")
    flash("Jotain meni pieleen, yritä uudestaan.", "error")
    return redirect("/newcocktail")

@app.route("/addalcohol", methods=["POST"])
def addalcohol():
    if request.method == "POST":
        alcohol = request.form["alcohol"]
        if request.form["amount"]:
            amount = int(request.form["amount"])
        else:
            amount = 1
        if cocktail.addalcohol(alcohol, amount):
            session["added_ingredients"] = cocktail.addalcohol(alcohol, amount)
            return redirect("/newcocktail")
    flash("Jotain meni pieleen, yritä uudestaan.", "error")
    return redirect("/newcocktail")

@app.route("/reset")
def reset():
    if request.method == "GET":
        if cocktail.reset():
            return redirect("/newcocktail")
    flash("Jotain meni pieleen, yritä uudestaan.", "error")
    return redirect("/newcocktail")

@app.route("/addingredient")
def addingredient():
    if not check_user():
        flash("Sinun tulee olla kirjautuneena sisään!", "error")
        return redirect("/")
    return render_template("addingredient.html")

@app.route("/newingredient", methods=["POST"])
def newingredient():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    name = request.form["name"]
    is_alc = request.form["is_alc"]
    if cocktail.newingredient(name, is_alc):
        flash("Uusi ainesosa lisätty listalle!", "message")
        return redirect("/newcocktail")
    else:
        flash("Hups, jotain meni pieleen :(. Varmista ettei ainesosaa ole jo olemassa!", "error")
        return redirect("/addingredient")

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
            if password1 == password2:
                if users.createuser(username, password1):
                    flash("Käyttäjä luotu!", "message")
                    return redirect("/")
                else:
                    flash("Jotain meni pieleen tai käyttänimi on jo käytössä", "error")
            else:
                flash("Salasanat eivät täsmää.", "error")
                return redirect("/newuser")
    flash("Käyttäjänimi tai salasana ei kelpaa", "error")
    return render_template("newuser.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("userlogin.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            flash("Olet kirjautunut sisään!", "message")
            return redirect("/")
        else:
            flash("Tarkista käyttäjänimi tai salasana!", "error")
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
    flash("Hakusana on liian lyhyt tai pitkä", "error")
    return redirect("/")