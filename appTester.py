import os
import numpy as np
import pandas as pd
import PIL as Image
import cv2
import json
from DeepImageSearch import LoadData, SearchImage

from flask import Flask, flash, request, redirect, url_for, render_template
from wtforms import FileField, SubmitField
import pickle
import urllib.request
from werkzeug.utils import secure_filename
from collections import OrderedDict

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/ipImages'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'PNG'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# load the dataset and image names
image_list = LoadData().from_folder(folder_list=['static/images'])
data = pd.read_csv("listings.csv")

name_list = data['name'].tolist()
desc_list = data['description'].tolist()
cap_list = data['accommodates'].tolist()
book_list = data['listing_url'].tolist()
price_list = data['price'].tolist()
tag_list = data['amenities'].tolist()
rating_list = data['review_scores_rating'].tolist()
numRating_list = data['number_of_reviews'].tolist()
roomType_list = data['room_type'].tolist()
bed_list = data['beds'].tolist()

# take image input
# print("CSE3013 Artificial Intelligence Project Review 2")
# print("Title: Hotel Room Recommendation System Using Image Similarity")
# print("Team Members:\n19BCI0001: Dayeem Parkar\n19BCI0036: Akashdeep\n19BCE0891: Anmol")
matches, fNames, ipFile = 20, OrderedDict(), ""


# default page of our web-app
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_user():
    return render_template('register.html', msg=(request.form['username'] + ' Registered Successfully'))


@app.route('/hotel')
def home():
    return render_template('hotel.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/hotel', methods=['POST'])
def upload_image():
    global fNames, ipFile
    filteredDict = fNames
    if 'fromLogin' in request.form:
        return render_template('hotel.html')

    # Check if it is filter form
    if 'filter' in request.form:
        # filter room for
        roomFor = int(request.form['roomfor'])
        filteredDict = OrderedDict(filter(lambda elem: roomFor == int(elem[1][7]), filteredDict.items()))

        # filter beds
        beds = int(request.form['beds'])
        filteredDict = OrderedDict(filter(lambda elem: beds <= int(elem[1][9]), filteredDict.items()))

        isValid = True
        rating = 0
        # filter rating
        try:
            rating = float(request.form['rating'])
        except ValueError:
            isValid = False
        if isValid:
            rating = min(5, rating)
            filteredDict = OrderedDict(filter(lambda elem: rating <= elem[1][4], filteredDict.items()))

        print(beds)
        # filter price
        isValid = True
        try:
            minP, maxP = float(request.form['minP']), float(request.form['maxP'])
        except ValueError:
            isValid = False
        if isValid and minP <= maxP:
            filteredDict = OrderedDict(filter(lambda elem: minP <= float(elem[1][3][1:]) <= maxP, filteredDict.items()))

        # print(filteredDict)
        # filter room type
        rType = request.form.getlist('cb1')
        if len(rType) > 0:
            filteredDict = OrderedDict(filter(lambda elem: elem[1][8] in rType, filteredDict.items()))

        # print(filteredDict)
        # filter amenities
        amen = request.form.getlist('cb2')
        # print(amen)
        if len(amen) > 0:
            filteredDict = OrderedDict(filter(lambda elem: all(x in elem[1][6] for x in amen), filteredDict.items()))

        # sort result
        sortBy = int(request.form.get('sortBy'))
        if sortBy == 2:
            filteredDict = OrderedDict(sorted(filteredDict.items(), key=lambda x: float(x[1][3][1:])))
        elif sortBy == 3:
            filteredDict = OrderedDict(sorted(filteredDict.items(), key=lambda x: float(x[1][3][1:]), reverse=True))
        elif sortBy == 4:
            filteredDict = OrderedDict(sorted(filteredDict.items(), key=lambda x: x[1][4], reverse=True))
        elif sortBy == 5:
            filteredDict = OrderedDict(sorted(filteredDict.items(), key=lambda x: x[1][4]))

        # print(filteredDict)
        return render_template('hotel.html', msg1="Image Provided For Search", msg2="Recommended For You",
                               ipFile=ipFile, filenames=filteredDict)

    # For rendering results on HTML GUI
    # find best matches
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        result = SearchImage().get_similar_images("static/ipImages/" + filename, number_of_images=matches)
        fNames, ipFile = OrderedDict(), filename
        print("\nBest room matches are: ")
        for key in result.keys():
            tags = tag_list[key].strip(']["').split('", "')[:8]
            print(result[key][14:])
            fNames[result[key][14:]] = [name_list[key], desc_list[key], book_list[key],
                                       price_list[key], float(rating_list[key]), numRating_list[key],
                                       tags, cap_list[key], roomType_list[key],
                                       int(bed_list[key])]

        sortBy = int(request.form.get('sortBy'))
        if sortBy == 1:
            filteredDict = fNames
        elif sortBy == 2:
            filteredDict = OrderedDict(sorted(fNames.items(), key=lambda x: float(x[1][3][1:])))
        elif sortBy == 3:
            filteredDict = OrderedDict(sorted(fNames.items(), key=lambda x: float(x[1][3][1:]), reverse=True))
        elif sortBy == 4:
            filteredDict = OrderedDict(sorted(fNames.items(), key=lambda x: x[1][4], reverse=True))
        else:
            filteredDict = OrderedDict(sorted(fNames.items(), key=lambda x: x[1][4]))
        return render_template('hotel.html', msg1="Image Provided For Search", msg2="Recommended For You",
                               ipFile=filename, filenames=filteredDict)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/hotel/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='images/' + filename), code=301)


@app.route('/displayIp/<filename>')
def display_ipImage(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='ipImages/' + filename), code=301)


if __name__ == "__main__":
    app.run(debug=True)
