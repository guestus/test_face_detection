from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
import cv2
import imagezmq
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from threading import current_thread,Lock

livestreaming = Blueprint('livestreaming', __name__)

cam = cv2.VideoCapture(0)

def gen_frames():
    receiver = imagezmq.ImageHub(open_port='tcp://localhost:5555', REQ_REP = False)
    while True:
        # Pull an image from the queue
        camName, frame = receiver.recv_image()
        # Using OpenCV library create a JPEG image from the frame we have received
        jpg = cv2.imencode('.jpg', frame)[1]
        # Convert this JPEG image into a binary string that we can send to the browser via HTTP
        yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg.tostring()+b'\r\n'

@livestreaming.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@livestreaming.route('/livestreaming', methods=['GET', 'POST'])
@login_required
def getmytable():
    return render_template("livestreaming.html", user=current_user, thread=current_thread().ident)