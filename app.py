from website import create_app
from flask import Flask
from threading import current_thread,Lock
from website import shared_stuff


app = create_app()
shared_stuff.lock = Lock()

    
if __name__ == '__main__':
    app.run(host='192.168.0.20', debug=True, port=5001)


