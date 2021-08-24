from website import create_app
from flask import Flask

app, x  = create_app()

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
    x.raise_exception()
    x.join()


