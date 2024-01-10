# src/config.py

class Config:
    SERVER_NAME = '10.0.0.71:5000'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    LED_PIN = 18
    LED_INVERT = False
    LED_CHANNEL = 0
    LED_COUNTS = 100
    LED_FREQS = 800000
    LED_DMAS = 5
    LED_BRIGHTNESSES = 100
    LED_STRIP_TYPES = 'WS2811_STRIP_GRB'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///light.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
