from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://uzcbqysykxnrgu:6710d725361c8f000bd2cf9d0444013410362cacd587f51be207f1ad89a8eab2@ec2-174-129-255-59.compute-1.amazonaws.com:5432/d176rtljvm3abj"

heroku = Heroku(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

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

class InventoryItem(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    location = db.Column(db.Integer, nullable=False)

    def __init__(self, name, weight, location):
        self.name = name
        self.weight = weight
        self.location = location

class ItemSchema(ma.Schema):
    class Meta:
        fields = ("id", "weight", "name", "location")

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

@app.route("/user/create", methods=["POST"])
def create_user():
    if request.content_type.startswith("application/json"):
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
    all_users = db.session.query(User.id, User.username, User.password).all()
    return jsonify(all_users)

@app.route("/user/verify", methods=["POST"])
def verify_user():
    print(request)
    print(request.content_type)
    if request.content_type.startswith("application/json"):
        post_data = request.get_json()
        username = post_data.get("username")
        password = post_data.get("password")

        hashed_password = db.session.query(User.password).filter(User.username == username).first()

        if hashed_password == None:
            return jsonify("NotValidated")

        validation = bcrypt.check_password_hash(hashed_password[0], password)

        if validation == True:
            return jsonify("Validated")
        return jsonify("NotValidated")
    return jsonify("Error: request must be sent as JSON")

@app.route("/user/delete/<id>", methods=["DELETE"])
def delete_user(id):
    record = db.session.query(User).filter(User.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify("User Deleted")

@app.route("/item/create", methods=["POST"])
def create_item():
    if request.content_type.startswith("application/json"):
        post_data = request.get_json()
        name = post_data.get("name")
        weight = post_data.get("weight")
        location = post_data.get("location")

        record = InventoryItem(name, weight, location)

        db.session.add(record)
        db.session.commit()

        return jsonify("Item Created")
    return jsonify("Error: request must be sent as JSON")

@app.route("/item/get/", methods=["GET"])
def get_all_items():
    all_items = db.session.query(InventoryItem).all()
    
    return jsonify(items_schema.dump(all_items))

@app.route("/item/delete/<id>", methods=["DELETE"])
def item_delete(id):
    record = db.session.query(InventoryItem).filter(InventoryItem.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify("Item Deleted")     


if __name__ == "__main__":
    app.debug = True
    app.run()