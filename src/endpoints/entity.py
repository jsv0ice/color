# src/endpoints/entity.py

from flask import Blueprint, request, jsonify, current_app
from ..util.has_cyclic_relationship import has_cyclic_relationship
from ..models import Entity, LightState
from ..database import db
import gc
from sqlalchemy import inspect


entity_bp = Blueprint('entity', __name__)

@entity_bp.route('/entity/', methods=['POST', 'PUT', 'DELETE', 'GET'])
def manage_entity():
    """
    Endpoint to create, update, delete, or retrieve entity information.

    Depending on the request method, different operations are performed:
    POST - Create a new entity
    PUT - Update an existing entity
    DELETE - Delete an entity
    GET - Retrieve entities. If a specific entity ID is provided, retrieves only that entity.

    Returns:
    Flask Response: JSON response indicating the success or failure of the operation.
    """

    # For GET requests, no JSON body is expected
    if request.method == 'GET':
        entity_id = request.args.get('id')
        if entity_id is None:
            return get_entities()
        else:
            return get_entity({'id': entity_id})

    # For POST, PUT, DELETE, the JSON body is expected
    data = request.json
    if request.method == 'POST':
        return create_entity(data)
    elif request.method == 'PUT':
        return update_entity(data)
    elif request.method == 'DELETE':
        return delete_entity(data)
    
def create_entity(data):
    """
    Create a new Entity in the database.

    Parameters:
    data (dict): A dictionary containing the following keys:
        - name (str): The name of the entity.
        - start_addr (int): The starting address of the entity.
        - end_addr (int): The ending address of the entity.
        - parent_id (int, optional): The ID of the parent entity, if any.

    Returns:
    Flask Response: JSON response indicating the success or failure of entity creation.
    """

    # Extracting required data from the input dictionary
    name = data.get('name')
    start_addr = data.get('start_addr')
    end_addr = data.get('end_addr')
    parent_id = data.get('parent_id')

    # Validating the presence of mandatory fields
    if None in (name, start_addr, end_addr):
        return jsonify({"error": "Missing data"}), 400

    # Check for parent entity if parent_id is provided
    if parent_id:
        parent_entity = Entity.query.filter_by(id=parent_id).first()
        if not parent_entity:
            return jsonify({"error": "Parent entity not found"}), 404

        # Validate to avoid cyclic relationships in the entity hierarchy
        if has_cyclic_relationship(parent_entity.id, parent_id):
            return jsonify({"error": "Invalid parent entity: cyclic relationship detected"}), 400

    # Creating a new entity with the given details
    new_entity = Entity(name=name, start_addr=start_addr, end_addr=end_addr, parent_id=parent_id)

    # Add the new entity to the database
    with current_app.app_context():
        db.session.add(new_entity)
        db.session.commit()

    # Fetch the newly created entity for confirmation
    entity = Entity.query.filter_by(name=name).order_by(Entity.id.desc()).first()

    # Create a default light state for the new entity
    new_state = LightState(entity_id=entity.id, is_on=False, red=0, green=0, blue=0, brightness=0)

    # Add the new light state to the database
    with current_app.app_context():
        db.session.add(new_state)
        db.session.commit()

    # Return a success response with the new entity's ID
    return jsonify({"success": "Entity created successfully", "id": entity.id}), 200

def update_entity(data):
    """
    Update an existing Entity in the database.

    Parameters:
    data (dict): A dictionary containing the following keys:
        - id (int): The ID of the entity to be updated.
        - name (str): The new name of the entity.
        - start_addr (int): The new starting address of the entity.
        - end_addr (int): The new ending address of the entity.
        - parent_id (int, optional): The ID of the new parent entity, if any.

    Returns:
    Flask Response: JSON response indicating the success or failure of the entity update.
    """

    # Extracting required data from the input dictionary
    entity_id = data.get('id')
    name = data.get('name')
    start_addr = data.get('start_addr')
    end_addr = data.get('end_addr')
    parent_id = data.get('parent_id')

    # Validating the presence of mandatory fields
    if None in (entity_id, name, start_addr, end_addr):
        return jsonify({"error": "Missing data"}), 400

    # Fetching the entity to be updated
    entity = Entity.query.filter_by(id=entity_id).first()
    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    # Update parent_id only if parent_id is provided
    if parent_id:
        parent_entity = Entity.query.filter_by(id=parent_id).first()
        if not parent_entity:
            return jsonify({"error": "Parent entity not found"}), 404

        # Check for cyclic relationship
        if has_cyclic_relationship(entity_id, parent_entity.id):
            return jsonify({"error": "Invalid parent entity: cyclic relationship detected"}), 400

        entity.parent_id = parent_id
    else:
        # If parent_id is not provided, set parent_id to None
        entity.parent_id = None

    # Updating the entity details
    entity.name = name
    entity.start_addr = start_addr
    entity.end_addr = end_addr

    # Committing the updates to the database
    with current_app.app_context():
        db.session.commit()

    # Return a success response after updating the entity
    return jsonify({"success": "Entity updated successfully"}), 200

def delete_entity(data):
    """
    Delete an existing Entity from the database.

    Parameters:
    data (dict): A dictionary containing the following key:
        - id (int): The ID of the entity to be deleted.

    Returns:
    Flask Response: JSON response indicating the success or failure of the entity deletion.
    """

    # Extracting the entity ID from the input dictionary
    entity_id = data.get('id')

    # Validating the presence of the entity ID
    if not entity_id:
        return jsonify({"error": "Missing data"}), 400



    # Deleting the entity from the database
    with current_app.app_context():
        # Fetching the entity to be deleted
        entity = Entity.query.filter_by(id=entity_id).first()
        if not entity:
            return jsonify({"error": "Entity not found"}), 404
        db.session.delete(entity)
        db.session.commit()

    # Return a success response after deleting the entity
        return jsonify({"success": "Entity deleted successfully"}), 200

def get_entities():
    """
    Retrieve all entities from the database along with their most recent light state.

    Returns:
    Flask Response: JSON response containing a list of all entities and their states.
    """

    # Fetching all entities from the database
    entities = Entity.query.all()
    entities_data = []

    for entity in entities:
        # Fetching the most recent light state for each entity
        entity_state = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()

        # Preparing the state data in JSON format
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

        # Preparing the entity data including its state
        entity_data = {
            "id": entity.id,
            "name": entity.name,
            "start_addr": entity.start_addr,
            "end_addr": entity.end_addr,
            "parent_id": entity.parent.id if entity.parent else None,
            "state": entity_state_json
        }

        entities_data.append(entity_data)

    # Return a response with the list of entities and their states
    return jsonify(entities_data), 200

def get_entity(entity_id):
    """
    Retrieve a single entity from the database along with its most recent light state.

    Parameters:
    entity_id (int): The ID of the entity to retrieve.

    Returns:
    Flask Response: JSON response containing the entity and its state.
    """

    # Fetch the entity by its ID
    entity = Entity.query.filter_by(id=entity_id).first()

    if not entity:
        return jsonify({"error": "Entity not found"}), 404

    # Fetch the most recent light state for the entity
    entity_state = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()

    # Preparing the state data in JSON format
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

    # Preparing the entity data including its state
    entity_data = {
        "id": entity.id,
        "name": entity.name,
        "start_addr": entity.start_addr,
        "end_addr": entity.end_addr,
        "parent_id": entity.parent.id if entity.parent else None,
        "state": entity_state_json
    }

    # Return a response with the entity and its state
    return jsonify(entity_data), 200
