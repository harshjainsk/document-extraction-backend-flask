from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


# INITIALIZE THE DATABASE
db = SQLAlchemy(app)

# create a database model

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

@app.route("/")
def test():
    return "hello world"


@app.route("/login", methods = ["POST", "GET"])
def user():

    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']

        # adding user to the database
        new_user = User(name=user_name, email = user_email, password = user_password)

        # push/ commit to the database
        try:
            db.session.add(new_user)
            db.session.commit()

        except Exception as e:
            print(e)
            return {"error" : "Please state the error, I also dont know"}
        
        return {
            "retrieved_email" : user_email,
            "retrieved_password" : user_password,
            "retrieved_name" : user_name
        }

    return "Login page"
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000, debug=True)
