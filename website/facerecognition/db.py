import sqlite3
import os
import np
import binascii
import cv2
import pickle
from datetime import datetime
#from collections import namedtuple
#from recordtype import recordtype
#class KnownFaces(namedtuple("Face", ["name", "key", "last_seen"])):
#    pass

class FacesDB:
    def __init__(self, dbfile):
        self.known_faces = list()#recordtype('Face', 'name key last_seen')
        db_is_new = not os.path.exists(dbfile)
        self.con = sqlite3.connect(dbfile)
        if db_is_new:
            sql= 'create table if not exists known_faces(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, picture BLOB, facekey TEXT KEY, last_seen FLOAT DEFAULT 0);'
            self.con.execute(sql)
            self.con.commit()
        else:
            sql = 'select name, facekey, last_seen from known_faces;'
            cur = self.con.cursor()
            for row in cur.execute(sql):
                enc_key=np.frombuffer(binascii.a2b_base64(row[1]), np.float32)
                self.known_faces.append([row[0],enc_key, row[2]])
                
    def add(self, key, picture, name, dt):
        if self.get(key)[0]==None:
            sql = 'INSERT INTO known_faces (name, picture, facekey) VALUES(?, ?, ?);'
            key_str = binascii.b2a_base64(key)
            self.con.execute(sql,[name, sqlite3.Binary(pickle.dumps(picture)), key_str])
            self.con.commit()
            self.known_faces.append([name,key, dt])

    def get(self, key):
        sql = 'select name, picture, last_seen from known_faces where facekey=?;'
        key_str = binascii.b2a_base64(key)
        cur = self.con.cursor()
        cur.execute(sql,[key_str])
        res=cur.fetchall()
        if len(res)==1:
            return res[0][0], pickle.loads(res[0][1]), res[0][2]
        else:
            return None,None,None

    def update_last_seen(self, key, dt):
        sql = 'update known_faces set last_seen=? where facekey=?'
        key_str = binascii.b2a_base64(key)
        self.con.execute(sql, [dt, key_str])
        self.con.commit()
        for i in self.known_faces:
            if (i[1] == key).all():
                i[2] = dt

#Test case
#img = cv2.imread('img28.jpeg', cv2.IMREAD_GRAYSCALE)
#f = FacesDB('faces.db')
#x = np.zeros((256), dtype=float)
#f.add(x,img,'test')
#sx1, sx2 = f.get(x)
#print(type(sx2))

#cv2.imshow('test',sx2)
#cv2.waitKey()
#print(len(f.known_faces[0].key))