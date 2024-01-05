import pytest
from flask import jsonify
from src import create_app, db
from src.models import Entity, LightState
from src.endpoints.entity import create_entity

@pytest.fixture
def app():
    app = create_app('testing')  # Replace 'testing' with the appropriate config name if different
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def new_entity_data():
    return {
        'name': 'New Entity',
        'start_addr': 100,
        'end_addr': 200,
        'parent_id': None
    }

def test_create_entity_valid_data(app, new_entity_data):
    with app.app_context():
        response = create_entity(new_entity_data)
        assert response[1] == 200
        data = response[0].json
        assert data['success'] == "Entity created successfully"
        assert 'id' in data

def test_create_entity_missing_data(app):
    with app.app_context():
        response = create_entity({'name': 'Incomplete Entity'})
        assert response[1] == 400
        assert 'Missing data' in response[0].json['error']

def test_create_entity_with_nonexistent_parent(app, new_entity_data):
    with app.app_context():
        new_entity_data['parent_id'] = 999  # Assuming 999 is a non-existent ID
        response = create_entity(new_entity_data)
        assert response[1] == 404
        assert 'Parent entity not found' in response[0].json['error']

def test_create_entity_with_cyclic_relationship(app, init_entities):
    with app.app_context():
        # Assuming entity 1 and 2 are already created by init_entities
        cyclic_data = {
            'name': 'Cyclic Entity',
            'start_addr': 300,
            'end_addr': 400,
            'parent_id': 1  # Creating a cyclic relationship
        }
        response = create_entity(cyclic_data)
        assert response[1] == 400
        assert 'Invalid parent entity: cyclic relationship detected' in response[0].json['error']
