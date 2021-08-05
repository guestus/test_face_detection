from website import create_app
from flask import Flask

app = create_app()

    
if __name__ == '__main__':
    app.run(host='192.168.0.20', debug=True, port=5001)


