
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from . import auth
    app.register_blueprint(auth.bp)

    return app


