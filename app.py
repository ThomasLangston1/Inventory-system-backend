from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = ""

heroku - Heroku(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(), nullable=False)
    phone = db.Column(db.Integer, nullable=True)

    def __init__(self, username, password, name, email, phone):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.phone = phone

@app.route("/user/create", methods=["POST"])
def create_user():
    if request.content_type == "application/json":
        post_data = request.get_json()
        username = post_data.get("username")
        password = post_data.get("password")
        name = post_data.get("name")
        email = post_data.get("email")
        phone = post_data.get("phone")

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        record = User(username, pw_hash, name, email, phone)     

        db.session.add(record)
        db.session.commit()

        return jsonify("User Created")  
    return jsonify("Error: requst must be sent as JSON")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User.id, User.username, Username.password).all()
    return jsonify(all_users)

@app.route("/user/verify", methods["POST"])
def verify_user():
    if request.content)type == "application/json":
        post_data = request.get_json()
        username = post_data.get("username")
        password = post_data.get("password")

        hashed_password = db.session.query(User.password).filter(User.username == username).first()

        if hashed_password == None:
            return jsonify("Uder Not validated")

        validation = bcrypt.check_password_hash(hashed_password[0], password)

        if validation == True:
            return jsonify("User Validated")
        return jsonify("User NOT Validated")
    return jsonify("Error: request must be sent as JSON")

if __name__ == "__main__":
    app.debug = True
    app.run()