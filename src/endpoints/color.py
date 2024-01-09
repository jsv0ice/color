# src/endpoints/entity.py

from flask import Blueprint, request, jsonify, current_app
from rpi_ws281x import Color
from ..util.update_light_state_for_entity_and_children import update_light_state_for_entity_and_children
from ..util.validate_color_values import validate_color_values
from ..models import Entity, LightState, Address
from ..database import db


color_bp = Blueprint('color', __name__)

@color_bp.route('/toggle/', methods=['POST'])
def toggle_light():
    """
    Endpoint to toggle the light state of a specified entity.

    Expects a JSON payload with the key 'entity'.

    Returns:
    Flask Response: JSON response indicating the success or failure of the toggle operation.
    """

    data = request.json
    entity_id = data.get('entity')

    # Validate entity presence
    if entity_id is None:
        return jsonify({"error": "Missing entity"}), 400

    # Fetch the entity by its ID
    entity = Entity.query.filter_by(id=entity_id).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    # Fetch the current light state
    current_state = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()
    if not current_state:
        return jsonify({"error": "No light state found for entity"}), 404

    # Toggle the light state
    is_on = not current_state.is_on

    # Update light state for entity
    with current_app.app_context():
        new_state = LightState(entity_id=entity.id, red=current_state.red, green=current_state.green, 
                               blue=current_state.blue, brightness=current_state.brightness, is_on=is_on)
        db.session.add(new_state)
        db.session.commit()

    # Apply the color to the LED strip
    if is_on is True:
        current_app.logger.info("current_state: " + str(current_state.red) + ", " + str(current_state.green) + ", " + str(current_state.blue) + ", " + str(current_state.brightness)
            + ", " + str(entity.start_addr) + ", " + str(entity.end_addr))
        colorWipe(current_app.strip, Color(current_state.red, current_state.green, current_state.blue), 
                  int(current_state.brightness), entity.start_addr, entity.end_addr)
    if is_on is False:
        current_app.logger.info("turning off: " + str(entity.start_addr) + ", " + str(entity.end_addr))
        colorWipe(current_app.strip, Color(0, 0, 0), 0, entity.start_addr, entity.end_addr)

    return jsonify({"success": "Light state toggled successfully", "is_on": is_on, "start_addr": entity.start_addr, "end_addr": entity.end_addr, "entity_id": entity.id}), 200


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

    # Validate entity presence
    if entity_id is None:
        return jsonify({"error": "Missing entity"}), 400

    # Fetch the entity by its ID
    entity = Entity.query.filter_by(id=entity_id).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404
        
    try:
        red = int(data.get('red'))
        green = int(data.get('green'))
        blue = int(data.get('blue'))
        brightness = int(data.get('brightness'))
    except TypeError:
        existing = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()
        red = existing.red
        green = existing.green
        blue = existing.blue
        brightness = existing.brightness

    if data.get('is_on') == 'false' or data.get('is_on') == False or data.get('is_on') == None:
        is_on = False
    else:
        is_on = True

    # Validate color values
    if [red, green, blue, brightness]:
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
    if is_on is True:
        current_app.logger.info("current_state: " + str(current_state.red) + ", " + str(current_state.green) + ", " + str(current_state.blue) + ", " + str(current_state.brightness)
            + ", " + str(entity.start_addr) + ", " + str(entity.end_addr))
        colorWipe(current_app.strip, Color(current_state.red, current_state.green, current_state.blue), 
                  int(current_state.brightness), entity.start_addr, entity.end_addr)
    if is_on is False:
        current_app.logger.info("turning off: " + str(entity.start_addr) + ", " + str(entity.end_addr))
        colorWipe(current_app.strip, Color(0, 0, 0), 0, entity.start_addr, entity.end_addr)
    return jsonify({"success": "Color updated successfully"}), 200

#def colorWipe(strip, color, brightness, range_start, range_end, wait_ms=5):
#    for i in range(strip.numPixels()):
#        if i >= range_start and i <= range_end:
#            strip.setPixelColor(i, color)
#            strip.setBrightness(brightness)
#            strip.show()


def colorWipe(strip, new_color, new_brightness, range_start, range_end, wait_ms=5):
    with current_app.app_context():
        for i in range(strip.numPixels()):
            if range_start <= i <= range_end:
                color_to_set = new_color
                brightness_to_set = new_brightness
                # Update the in-memory data structure
                current_app.pixel_states[i] = {'red': new_color.r, 'green': new_color.g, 'blue': new_color.b, 'brightness': new_brightness}
            else:
                state = current_app.pixel_states[i]
                color_to_set = Color(state['red'], state['green'], state['blue'])
                brightness_to_set = state['brightness']

            # Set color and brightness for the pixel
            strip.setPixelColor(i, color_to_set)
            strip.setBrightness(brightness_to_set)
        strip.show()
        
        saveStateToDatabase()

def saveStateToDatabase():
    with current_app.app_context():
        for i, state in enumerate(current_app.pixel_states):
            address_record = Address.query.filter_by(id=i).first()
            if address_record:
                # Update existing record
                address_record.red = state['red']
                address_record.green = state['green']
                address_record.blue = state['blue']
                address_record.brightness = state['brightness']
            else:
                # Create a new record if it doesn't exist
                new_address = Address(id=i, red=state['red'], green=state['green'], blue=state['blue'], brightness=state['brightness'])
                db.session.add(new_address)

        db.session.commit()