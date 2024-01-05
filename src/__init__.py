# src/__init__.py

from flask import Flask ,current_app
from rpi_ws281x import PixelStrip, ws
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .endpoints.entity import entity_bp
from .endpoints.color import color_bp
from .database import db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(entity_bp, url_prefix='/entity')
    app.register_blueprint(color_bp, url_prefix='/color')

    db.init_app(app)

    with app.app_context():
        db.create_all()
        

    return app