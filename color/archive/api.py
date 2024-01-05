from uuid import uuid4
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import time
from rpi_ws281x import Color, PixelStrip, ws

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'light.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Fixed LED strip configuration
LED_PIN = 18
LED_INVERT = False
LED_CHANNEL = 0

# Permutation ranges and increments
led_counts = 100  # Modify as needed
led_freqs = 800000  # Modify as needed
led_dmas = 5  # Modify as needed
led_brightnesses = 100  # Modify as needed
led_strip_types = ws.WS2811_STRIP_GRB

def colorWipe(strip, color, brightness, range_start, range_end, wait_ms=5):
    for i in range(strip.numPixels()):
        if i >= range_start and i <= range_end:
            strip.setPixelColor(i, color)
            strip.setBrightness(brightness)
            strip.show()


class LightState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)
    is_on = db.Column(db.Boolean, default=False)
    red = db.Column(db.Integer, default=0)
    green = db.Column(db.Integer, default=0)
    blue = db.Column(db.Integer, default=0)
    brightness = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_addr = db.Column(db.Integer, nullable=False)
    end_addr = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)

    # Define the relationship (self-referential)
    parent = db.relationship('Entity', remote_side=[id], backref=db.backref('children', lazy='dynamic'))


# Initialize the database
with app.app_context():
    db.create_all()

def has_cyclic_relationship(start_uuid, current_uuid):
    if start_uuid == current_uuid:
        return True

    current_entity = Entity.query.filter_by(uuid=current_uuid).first()
    if current_entity and current_entity.parent:
        return has_cyclic_relationship(start_uuid, current_entity.parent.uuid)

    return False


#entity functions
def create_entity(data):
    name = data.get('name')
    start_addr = data.get('start_addr')
    end_addr = data.get('end_addr')
    parent_uuid = data.get('parent_uuid')

    if None in (name, start_addr, end_addr):
        return jsonify({"error": "Missing data"}), 400

    uuid = str(uuid4())
    parent_id = None
    if parent_uuid:
        parent_entity = Entity.query.filter_by(uuid=parent_uuid).first()
        if not parent_entity:
            return jsonify({"error": "Parent entity not found"}), 404

        if has_cyclic_relationship(uuid, parent_entity.uuid):
            return jsonify({"error": "Invalid parent entity: cyclic relationship detected"}), 400

        parent_id = parent_entity.id

    new_entity = Entity(uuid=uuid, name=name, start_addr=start_addr, end_addr=end_addr, parent_id=parent_id)

    with app.app_context():
        db.session.add(new_entity)
        db.session.commit()

    entity = Entity.query.filter_by(name=name).order_by(Entity.id.desc()).first()
    new_state = LightState(entity=entity.id, is_on=False, red=0, green=0, blue=0, brightness=0)

    with app.app_context():
        db.session.add(new_state)
        db.session.commit()

    return jsonify({"success": "Entity created successfully", "uuid": uuid}), 200

def update_entity(data):
    uuid = data.get('uuid')
    name = data.get('name')
    start_addr = data.get('start_addr')
    end_addr = data.get('end_addr')
    parent_uuid = data.get('parent_uuid')

    if None in (uuid, name, start_addr, end_addr):
        return jsonify({"error": "Missing data"}), 400

    entity = Entity.query.filter_by(uuid=uuid).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    # Update parent_id only if parent_uuid is provided
    if parent_uuid:
        parent_entity = Entity.query.filter_by(uuid=parent_uuid).first()
        if not parent_entity:
            return jsonify({"error": "Parent entity not found"}), 404

        # Check for cyclic relationship
        if has_cyclic_relationship(uuid, parent_entity.uuid):
            return jsonify({"error": "Invalid parent entity: cyclic relationship detected"}), 400

        entity.parent_id = parent_entity.id
    else:
        # If parent_uuid is not provided, set parent_id to None
        entity.parent_id = None

    entity.name = name
    entity.start_addr = start_addr
    entity.end_addr = end_addr

    with app.app_context():
        db.session.commit()

    return jsonify({"success": "Entity updated successfully"}), 200


def delete_entity(data):
    uuid = data.get('uuid')

    if not uuid:
        return jsonify({"error": "Missing data"}), 400

    entity = Entity.query.filter_by(uuid=uuid).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    with app.app_context():
        db.session.delete(entity)
        db.session.commit()

    return jsonify({"success": "Entity deleted successfully"}), 200

def get_entity(data):
    uuid = data.get('uuid')

    if not uuid:
        return jsonify({"error": "Missing data: " + str(data)}), 400

    entity = Entity.query.filter_by(uuid=uuid).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404
    
    entity_state = LightState.query.filter_by(entity=entity.id).order_by(LightState.timestamp.desc()).first()
    if entity_state:
        entity_state_json = {"is_on": entity_state.is_on, "red": entity_state.red, "green": entity_state.green, "blue": entity_state.blue, "brightness": entity_state.brightness}
    else:
        entity_state_json = {"is_on": False, "red": 0, "green": 0, "blue": 0, "brightness": 0}

    return jsonify({"uuid": entity.uuid, "name": entity.name, "start_addr": entity.start_addr, "end_addr": entity.end_addr, "parent_uuid": entity.parent.uuid if entity.parent else None, "state": entity_state_json}), 200

def get_entities():
    entities = Entity.query.all()
    entities_data = []

    for entity in entities:
        entity_state = LightState.query.filter_by(entity=entity.id).order_by(LightState.timestamp.desc()).first()
        if entity_state:
            entity_state_json = {
                "is_on": entity_state.is_on, 
                "red": entity_state.red, 
                "green": entity_state.green, 
                "blue": entity_state.blue, 
                "brightness": entity_state.brightness
            }
        else:
            entity_state_json = {"is_on": False, "red": 0, "green": 0, "blue": 0, "brightness": 0}

        entity_data = {
            "uuid": entity.uuid,
            "name": entity.name,
            "start_addr": entity.start_addr,
            "end_addr": entity.end_addr,
            "parent_uuid": entity.parent.uuid if entity.parent else None,
            "state": entity_state_json
        }

        entities_data.append(entity_data)

    return jsonify(entities_data), 200  

# Validation function for incoming color data
def validate_color_values(red, green, blue, brightness):
    if not all(isinstance(v, int) for v in [red, green, blue, brightness]):
        print("All values must be integers")
        return False, "All values must be integers"
    if not all(0 <= v <= 255 for v in [red, green, blue]):
        print("Red, Green, Blue values must be between 0 and 255")
        return False, "Red, Green, Blue values must be between 0 and 255"
    if not 1 <= brightness <= 255:
        print("Brightness must be between 1 and 255")
        return False, "Brightness must be between 1 and 255"
    return True, ""

def update_light_state_for_entity_and_children(entity_uuid, red, green, blue, brightness, is_on):
    entity = Entity.query.filter_by(uuid=entity_uuid).first()
    if not entity:
        return

    # Update the light state of the current entity
    current_state = LightState.query.filter_by(entity=entity.id).order_by(LightState.timestamp.desc()).first()
    if not current_state or any([current_state.is_on != is_on,
                                 current_state.red != red,
                                 current_state.green != green,
                                 current_state.blue != blue,
                                 current_state.brightness != brightness]):
        new_state = LightState(entity=entity.id, is_on=is_on, red=red, green=green, blue=blue, brightness=int(brightness/2.55))
        db.session.add(new_state)

    # Recursively update the light state of all child entities
    for child in entity.children:
        update_light_state_for_entity_and_children(child.uuid, red, green, blue, brightness, is_on)

@app.route('/color/', methods=['POST'])
def set_color():
    data = request.json
    entity_uuid = data.get('entity')
    red = int(data.get('red'))
    green = int(data.get('green'))
    blue = int(data.get('blue'))
    brightness = int(data.get('brightness'))
    is_on = data.get('is_on') == 'true'  # Convert to boolean

    if entity_uuid is None:
        return jsonify({"error": "Missing entity"}), 400

    entity = Entity.query.filter_by(uuid=entity_uuid).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    if None in (red, green, blue, brightness, is_on):
        return jsonify({"error": "Missing color data"}), 400

    valid, message = validate_color_values(red, green, blue, brightness)
    if not valid:
        return jsonify({"error": message}), 400
    
    current_state = LightState.query.filter_by(entity=entity.id).order_by(LightState.timestamp.desc()).first()

    if current_state and not any([current_state.is_on != is_on,
                                  current_state.red != red,
                                  current_state.green != green,
                                  current_state.blue != blue,
                                  current_state.brightness != brightness]):
        return jsonify({"success": "Color already set"}), 200
        
    # Update light state for entity and its children
    with app.app_context():
        update_light_state_for_entity_and_children(entity_uuid, red, green, blue, brightness, is_on)
        db.session.commit()

    colorWipe(strip, Color(red, green, blue), int(brightness/2.55), entity.start_addr, entity.end_addr)
    return jsonify({"success": "Color updated successfully"}), 200  

@app.route('/entity/', methods=['POST', 'PUT', 'DELETE', 'GET'])
def makeentity():
    data = request.json
    if request.method == 'POST':
        return create_entity(data)
    elif request.method == 'PUT':
        return update_entity(data)
    elif request.method == 'DELETE':
        return delete_entity(data)
    elif request.method == 'GET':
        if data.get('uuid') == None:
            return get_entities()
        return get_entity(data)    
            
if __name__ == '__main__':
    strip = PixelStrip(led_counts, LED_PIN, led_freqs, led_dmas, LED_INVERT, 100, LED_CHANNEL, led_strip_types)
    strip.begin()
    app.run(debug=True, host='0.0.0.0')

