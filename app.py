from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///document-extraction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create an instance of bcrypt
bcrypt = Bcrypt(app)

# INITIALIZE THE DATABASE
db = SQLAlchemy(app)

# create a database model

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)


class AddImage(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String)
    data = db.Column(db.LargeBinary)
    

@app.route("/")
def test():
    return "hello world"


@app.route("/login", methods = ["POST", "GET"])
def user():

    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']

        encrypted_password = bcrypt.generate_password_hash(user_password)

        # adding user to the database
        new_user = User(name=user_name, email = user_email, password = encrypted_password)

        # push/ commit to the database
        try:
            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            print(e)
            return {"error" : f"{e}"}
        
        return {
            "retrieved_email" : str(user_email),
            "retrieved_password" : str(user_password),
            "retrieved_name" : str(user_name)
        }

    return "Login page"


@app.route("/uploadImage", methods = ["GET", "POST"])
def uploadImage():

    if request.method == 'POST':
        file = request.files['file']

        new_file_upload = AddImage(filename = file.filename, data = file.read())
        db.session.add(new_file_upload)
        db.session.commit()
        list_of_images = AddImage.query.all()
        # print(list_of_images)
        for i in list_of_images:
            print(i.filename)
        return {"Uploaded" : f"{file.filename}"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000, debug=True)
