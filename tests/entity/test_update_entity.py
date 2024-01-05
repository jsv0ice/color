import pytest
from flask import jsonify
from ...src import create_app, db
from ...src.models import Entity
from ...src.endpoints.entity import update_entity

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
def init_entity(app):
    with app.app_context():
        entity = Entity(id=1, name="Original Entity", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()
        return entity.id

def test_update_entity_valid_data(app, init_entity):
    with app.app_context():
        entity = db.session.get(Entity, init_entity)
        updated_data = {
            'id': entity.id,
            'name': 'Updated Entity',
            'start_addr': 150,
            'end_addr': 250,
            'parent_id': None
            }
        response = update_entity(updated_data)
        assert response[1] == 200
        assert 'Entity updated successfully' in response[0].json['success']

        updated_entity = db.session.get(Entity, entity.id)
        assert updated_entity.name == 'Updated Entity'
        assert updated_entity.start_addr == 150
        assert updated_entity.end_addr == 250

def test_update_entity_not_found(app, init_entity):
    with app.app_context():
        entity = db.session.get(Entity, init_entity)
        updated_data = {
            'id': 999,  # Non-existent entity ID
            'name': 'Updated Entity',
            'start_addr': 150,
            'end_addr': 250,
            'parent_id': None
        }
        response = update_entity(updated_data)
        assert response[1] == 404
        assert 'Entity not found' in response[0].json['error']

def test_update_entity_invalid_data(app, init_entity):
    
    with app.app_context():
        entity = db.session.get(Entity, init_entity)
        updated_data = {
            'id': entity.id,
            'name': None,  # Invalid data
            'start_addr': 150,
            'end_addr': 250,
            'parent_id': None
        }
        response = update_entity(updated_data)
        assert response[1] == 400
        assert 'Missing data' in response[0].json['error']