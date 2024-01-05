import pytest
from flask import jsonify
from ...src import create_app, db
from ...src.models import Entity, LightState
from ...src.endpoints.entity import create_entity

@pytest.fixture
def app():
    app = create_app() 
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

def test_create_entity_with_cyclic_relationship(app):
    with app.app_context():
        # Create the first entity
        entity1 = Entity(name="Entity1", start_addr=1, end_addr=10, parent_id=None)
        db.session.add(entity1)
        db.session.commit()

        # Create the second entity with the first entity as its parent
        entity2 = Entity(name="Entity2", start_addr=11, end_addr=20, parent_id=entity1.id)
        db.session.add(entity2)
        db.session.commit()

        # Create the cyclic relationship data
        cyclic_data = {
            'name': 'Cyclic Entity',
            'start_addr': 300,
            'end_addr': 400,
            'parent_id': entity1.id  # Referencing the first entity to create a cycle
        }

        # Perform the action that is supposed to detect the cycle
        response = create_entity(cyclic_data)

        # Assertions to verify the correct behavior
        assert response[1] == 400
        assert 'Invalid parent entity: cyclic relationship detected' in response[0].json['error']

        # Optionally, clean up by deleting the created entities
        db.session.delete(entity2)
        db.session.delete(entity1)
        db.session.commit()

