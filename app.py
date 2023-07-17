from flask import Flask, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

from model_utils import allowed_file, extract_details_from_aadhar, get_cropped_image

import numpy as np
from PIL import Image
import cv2
import torch
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR,draw_ocr


model = torch.hub.load('ultralytics/yolov5', 'custom', path = '150-epochs-best.pt', force_reload = True)
ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
names = ['aadhar card', 'driving license', 'pan card', 'salary slip', 'voter id']


def give_detection_results(image):
    image = cv2.resize(image, (640, 640))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(image)
    print(results)
    # return results
    print(results)
    bbox = results.xyxy[0][0]
    cropped_image = get_cropped_image(image, bbox)
    detected_class = int(results.xyxy[0][0][-1])
    detected_class = names[detected_class]
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
    result = ocr.ocr(cropped_image, cls=True)
    extraction = ""
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            extraction += line[-1][0]
            extraction += ' '
    print(extraction)

    if detected_class == 'aadhar card':
        info = extract_details_from_aadhar(extraction)
    elif detected_class == 'driving license':
        info = extract_details_from_aadhar(extraction)
    elif detected_class == 'pan card':
        return extraction
    elif detected_class == 'salary slip':
        info = extract_details_from_aadhar(extraction)
    else:
        info = extract_details_from_aadhar(extraction)


    return info


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
    

@app.route('/extract_details', methods = ['GET',"POST"])
def extract_details():
    if request.method == 'POST':
        file = request.files['file']

        if allowed_file(file.filename):

            image = Image.open(file)
            image_array = np.array(image)

            info = give_detection_results(image_array)
            print(info)
            return {
                "info_extracted" : info
            }


            # new_file_upload = AddImage(filename = file.filename, data = file.read())
            # db.session.add(new_file_upload)
            # db.session.commit()
            # list_of_images = AddImage.query.all()
            # # print(list_of_images)
            # for i in list_of_images:
            #     print(i.filename)
            # return {"Uploaded" : f"{file.filename}"}

    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000, debug=True)
