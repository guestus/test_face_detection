import db
import cv2
import numpy as np
import os
from os.path import isfile, join
import pathlib
from tqdm import tqdm
from scipy.spatial.distance import cosine
from PIL import Image
import np
import platform
import PIL
from datetime import datetime
import imagezmq
import notificator
from threading import Thread
import config






 
 
class FaceRecognitionThread(Thread):
    def __init__(self, cap_source, needPreload = False, skipframes = 5, conf_threshold = 0.90):
        """Инициализация потока"""
        Thread.__init__(self)
        self.cap_source = cap_source
        self.skipframes = skipframes
        self.conf_threshold = conf_threshold
        self.needPreload = needPreload

    def do_init(self):
        self.faceDB = db.FacesDB('faces.db')
        print(f'loaded {len(self.faceDB.known_faces)} faces')
        self.sender = imagezmq.ImageSender(connect_to = 'tcp://*:5555', REQ_REP = False)
        self.notify = notificator.TelegrammNotificator(chatid=config.chatid, auth=config.auth)
        #notify.sendMessage('Started.')

    def do_preload(self):
        data_root= join(pathlib.Path().resolve(),'data\\')
        assert os.path.exists(data_root)
        print (f"Data root: {data_root}")
        onlyfiles = [f for f in os.listdir(data_root) if isfile(join(data_root, f))]
        embedding = np.zeros(512)
        for idx, file in enumerate(tqdm(onlyfiles, "Create embeddings matrix", total=len(onlyfiles))):
            if (platform.system()=='Windows'):
                pil_img = Image.open(join(data_root,file))
                img = np.array(pil_img)
            else:
                img = cv2.imread(join(data_root,file))
            img = cv2.resize(img, (112,112), interpolation=cv2.INTER_LINEAR)
            blob = cv2.dnn.blobFromImage(img, 1.0/128.0, (112, 112), [128, 128, 128], swapRB=False, crop=False)
            self.bb.setInput(blob)
            key = self.bb.forward().squeeze(axis=0)
            key = key/np.linalg.norm(key)
            self.faceDB.add(key,img,os.path.splitext(file)[0],None)

    def _mainloop_(self):
        self.do_init()
        self.face = cv2.dnn.readNetFromTensorflow('checkpoint/opencv_face_detector_uint8.pb','checkpoint/opencv_face_detector.pbtxt')
        self.bb = cv2.dnn.readNetFromONNX('checkpoint/model.onnx')
        if self.needPreload:
            do_preload()
        facenum=0
        vcap = cv2.VideoCapture(self.cap_source)
        while(1):
            for i in range(self.skipframes):
                ret, frame = vcap.read()
            if ret==0:
               vcap = cv2.VideoCapture(self.cap_source)
               ret, frame = vcap.read()
            try:
                frame = cv2.resize(frame,(800,600),interpolation=cv2.INTER_LINEAR)
            except:
                print ('none frames recieved.')
                continue
            blob = cv2.dnn.blobFromImage(frame, 1.0, (600, 600), [104, 117, 123], swapRB=False, crop=False)  #[104,117, 123]
            self.face.setInput(blob)
            detections = self.face.forward()
            known_faces_found = 0
            for i in range(detections.shape[2]):
                confidence = detections[0,0,i,2]
                if confidence > self.conf_threshold:
                    now = datetime.now().timestamp()
                    x1 = int(detections[0,0,i,3]*frame.shape[1]*0.97)
                    y1 = int(detections[0,0,i,4]*frame.shape[0]*0.95)
                    x2 = int(detections[0,0,i,5]*frame.shape[1]*1.05)
                    y2 = int(detections[0,0,i,6]*frame.shape[0]*1.05)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    try:
                        detected_face = cv2.resize(frame[y1:y2,x1:x2],(112,112),interpolation=cv2.INTER_LINEAR)
                    except:
                        detected_face = None
                    if not (detected_face is None):
                        blob = cv2.dnn.blobFromImage(detected_face, 1/128.0, (112, 112), [128,128,128], swapRB=False, crop=False)  #[104,117, 123]
                        self.bb.setInput(blob)
                        emb= self.bb.forward().squeeze(axis=0)
                        emb = emb/np.linalg.norm(emb)
                        max_distance = -100
                        for kf in self.faceDB.known_faces:
                            distance= 1-cosine(emb, kf[1])
                            #distance = emb @ kf.key.T
                            if max_distance<distance:
                                max_distance=distance
                                recognized_face = kf
                        if  max_distance>=0.5:
                            print(f'face at {now}: {recognized_face[0]}, last seen {now-recognized_face[2]} seconds ago.')
                            cv2.putText(frame, f"{recognized_face[0]}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX,  1, (255, 255, 255), 2, cv2.LINE_AA)
                            if (now - recognized_face[2])>5:
                                known_faces_found+= 1
                                #cv2.imshow('face'+str(i), detected_face)
                                #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            self.faceDB.update_last_seen(recognized_face[1], now)
                            print(f'update {recognized_face[0]} to now.')
                        else:
                            pass
                            #cv2.imwrite(f"unk{facenum}.jpg",detected_face)
                            #self.faceDB.add(emb,detected_face,f"unk{facenum}", now)
                            #facenum += 1
            if known_faces_found>0:
                #cv2.imwrite(f"file-temp.jpg",frame)
                #try:
                #    bot.sendPhoto('-598402664',open(f"file-temp.jpg",'rb'))
                #except:
                #    print("failed to send")
                #os.remove(f"file-temp.jpg")
                self.notify.sendImage(frame)
            #cv2.imshow('VIDEO', frame)
            self.sender.send_image("VIDEO", frame)

    def run(self):
        self._mainloop_()



