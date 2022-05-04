from db import db
from flask import session

added_ingredients = {}

def get_cocktails():
    sql = db.session.execute("SELECT name FROM recipes")
    recipes = sql.fetchall()
    return recipes

def get_ingredient_list():
    sql0 = db.session.execute("SELECT name FROM ingredient WHERE is_alc = TRUE ORDER BY name ASC")
    alcohols = sql0.fetchall()
    sql1 = db.session.execute("SELECT name FROM ingredient WHERE is_alc = FALSE ORDER BY name ASC")
    mixers = sql1.fetchall()
    return alcohols, mixers, added_ingredients

def makecocktail(name, desc):
    print(added_ingredients)
    try:
        sql0 = "INSERT INTO recipes (name,description) VALUES (:name,:description) RETURNING id"
        result = db.session.execute(sql0, {"name":name, "description":desc})
        recipe_id = result.fetchone()
        sql2 = "INSERT INTO recipe_ingredient (ingredient_id, recipe_id, amount) VALUES (:ing_id,:rec_id,:amount)"
        for ingredient in added_ingredients:
            sql1 = "SELECT id FROM ingredient WHERE name = (:name)"
            sql1ex = db.session.execute(sql1, {"name":ingredient})
            ing_id = sql1ex.fetchone()
            amount = added_ingredients[ingredient]
            db.session.execute(sql2,{"ing_id":ing_id.id,"rec_id":recipe_id.id,"amount":amount})
        db.session.commit()
        return True
    except:
        return False     

def get_cocktail_info(cocktailname):
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
    
    return ingredients, desc, reviews

def leave_review(content, rating):
    user_id = session.get("user_id")
    recipe_id = session.get("recipe_id")
    try:
        sql = "INSERT INTO reviews (content, user_id, recipe_id, rating, sent_at) VALUES (:content, :user_id, :recipe_id, :rating, NOW())"
        db.session.execute(sql, {"content":content,"user_id":user_id,"recipe_id":recipe_id,"rating":rating})
        db.session.commit()
    except:
        return False
    return True
    
def addmixer(mixer, amount):
    added_ingredients[mixer]=amount

def addalcohol(alcohol, amount):
    added_ingredients[alcohol]=amount

def reset():
    added_ingredients.clear()
    
def get_added_ingredients():
    return added_ingredients

def newingredient(name, is_alc):
    try:
        sql = "INSERT INTO ingredient (name,is_alc) VALUES (:name,:is_alc)"
        db.session.execute(sql,{"name":name,"is_alc":is_alc})
        db.session.commit()
    except:
        return False
    return True