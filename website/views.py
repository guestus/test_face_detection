from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json
from . import facerecognition
import sqlite3
import pickle
import cv2
import base64
from datetime import datetime
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    con = sqlite3.connect('website/facerecognition/faces.db')
    sql = 'select name, last_seen, picture from known_faces order by last_seen desc;'
    cur = con.cursor()
    data=[]
    for x in cur.execute(sql):
        img = cv2.cvtColor(pickle.loads(x[2]),cv2.COLOR_BGR2RGB)
        jpg = cv2.imencode('.jpg', img)[1]
        image = f'data:image/jpeg;base64, {base64.b64encode(jpg).decode()}'
        data.append([x[0],datetime.fromtimestamp(x[1]).strftime("%Y-%m-%d %H:%M:%S"),image])
    return render_template("home.html", user=current_user, table=data)

