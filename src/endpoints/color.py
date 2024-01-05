# src/endpoints/entity.py

from flask import Blueprint, request, jsonify, current_app
from rpi_ws281x import Color
from ..util.update_light_state_for_entity_and_children import update_light_state_for_entity_and_children
from ..util.validate_color_values import validate_color_values
from ..models import Entity, LightState
from ..database import db


color_bp = Blueprint('color', __name__)

@color_bp.route('/color/', methods=['POST'])
def set_color():
    """
    Endpoint to set the color for a specified entity and its children.

    Expects a JSON payload with keys 'entity', 'red', 'green', 'blue', 'brightness', and 'is_on'.

    Returns:
    Flask Response: JSON response indicating the success or failure of the color update.
    """

    data = request.json
    entity_id = data.get('entity')
    red = int(data.get('red'))
    green = int(data.get('green'))
    blue = int(data.get('blue'))
    brightness = int(data.get('brightness'))
    is_on = data.get('is_on') == 'true'  # Convert to boolean

    # Validate entity presence
    if entity_id is None:
        return jsonify({"error": "Missing entity"}), 400

    # Fetch the entity by its ID
    entity = Entity.query.filter_by(id=entity_id).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    # Validate presence of color data
    if None in (red, green, blue, brightness, is_on):
        return jsonify({"error": "Missing color data"}), 400

    # Validate color values
    valid, message = validate_color_values(red, green, blue, brightness)
    if not valid:
        return jsonify({"error": message}), 400
    
    # Check current state before updating
    current_state = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()
    if current_state and not any([current_state.is_on != is_on,
                                  current_state.red != red,
                                  current_state.green != green,
                                  current_state.blue != blue,
                                  current_state.brightness != brightness]):
        return jsonify({"success": "Color already set"}), 200
        
    # Update light state for entity and its children
    with current_app.app_context():
        update_light_state_for_entity_and_children(entity_id, red, green, blue, brightness, is_on)
        db.session.commit()

    # Apply the color to the LED strip
    colorWipe(current_app.strip, Color(red, green, blue), int(brightness/2.55), entity.start_addr, entity.end_addr)
    return jsonify({"success": "Color updated successfully"}), 200

def colorWipe(strip, color, brightness, range_start, range_end, wait_ms=5):
    for i in range(strip.numPixels()):
        if i >= range_start and i <= range_end:
            strip.setPixelColor(i, color)
            strip.setBrightness(brightness)
            strip.show()