import pytest
import json
from flask import url_for
from ...src import create_app, db  # Update the import path
from ...src.models import Entity, LightState  # Update the import path
from ...src.endpoints.color import set_color  # Update the import path

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
def init_entity(app):
    with app.app_context():
        entity = Entity(id=1, name="Test Entity", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()
        return entity

def test_set_color_valid(client, init_entity):
    data = {
        'entity': init_entity.id,
        'red': 255,
        'green': 100,
        'blue': 50,
        'brightness': 200,
        'is_on': 'true'
    }
    response = client.post(url_for('set_color'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert 'Color updated successfully' in response.json['success']

def test_set_color_missing_entity(client, init_entity):
    data = {
        'red': 255,
        'green': 100,
        'blue': 50,
        'brightness': 200,
        'is_on': 'true'
    }
    response = client.post(url_for('set_color'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert 'Missing entity' in response.json['error']

def test_set_color_entity_not_found(client):
    data = {
        'entity': 999,  # Non-existent entity ID
        'red': 255,
        'green': 100,
        'blue': 50,
        'brightness': 200,
        'is_on': 'true'
    }
    response = client.post(url_for('set_color'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 404
    assert 'Entity not found' in response.json['error']

# Additional tests for invalid color data can be added similarly

# Replace 'color' with the actual package name.
