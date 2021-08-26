# Face recoginition pet project

This is sample project with flask, opencv, zmq usage. The idea of this project is realtime known faces detection with live streaming through webpage. Faces with their embeddings are stored in mysqlite3 database. Also last detection time stored in the database.

When known face detected notification to telegram group happen.

Flask do autorization and streaming clent part. Also shows all known faces.

All nn models used with DNN opencv module:
- face recognition - pretrained IRSE IR50 converted to ONNX
- face detection - pretrained model from opencv 3dparty (
Quantized OpenCV face detection network)

## Usage
pre requirements:
- put pretrained models in website/facerecognition/checkpoint folder
- make website/facerecognition/config.py config file such is:
```python
camera_url = 'rtsp://login:password@ipaddr:554/ch01'
chatid='telegram chat id'
auth='telegram auth token'
```
- Put example jpg faces in /website/facerecognition/data folder. File name represents face name. Images are preffered at 112x112 resolution.
- Web interface availiable on 5001 port.
- After registration tou can whatch live stream.

## License
[MIT](https://choosealicense.com/licenses/mit/)
