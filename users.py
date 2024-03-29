import secrets
from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

def createuser(username, password):
    password = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (name,password,is_admin) VALUES (:name,:password,FALSE)"
        db.session.execute(sql,{"name":username,"password":password})
        db.session.commit()
    except:
        return False
    return True

def login(username, password):
    sql = "SELECT id, password FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()    
    if not user:
        return False
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["user_id"] = user[0]
            session["csrf_token"] = secrets.token_hex(16)

            return True
        else:
            return False

def logout():
    del session["username"]