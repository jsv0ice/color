
from src import create_app
from flask import Flask ,current_app
from rpi_ws281x import PixelStrip, ws
from flask_socketio import SocketIO
from .src.socket import socketio

app = create_app()


def initialize_led_strip():
    # Access the configuration from current_app.config
    led_counts = current_app.config['LED_COUNTS']
    led_pin = current_app.config['LED_PIN']
    led_freqs = current_app.config['LED_FREQS']
    led_dmas = current_app.config['LED_DMAS']
    led_invert = current_app.config['LED_INVERT']
    led_brightness = current_app.config['LED_BRIGHTNESSES']
    led_channel = current_app.config['LED_CHANNEL']
    led_strip_types = getattr(ws, current_app.config['LED_STRIP_TYPES'])

    # Initialize the LED strip
    strip = PixelStrip(led_counts, led_pin, led_freqs, led_dmas, led_invert, led_brightness, led_channel, led_strip_types)
    strip.begin()
    return strip


if __name__ == '__main__':
    with app.app_context():
        app.strip = initialize_led_strip()
        app.pixel_states = [{'red': 0, 'green': 0, 'blue': 0, 'brightness': 0} for _ in range(app.strip.numPixels())]

    # Run the Flask app
    socketio.run(debug=True, host='0.0.0.0')
