import pytest
import json
from flask import url_for
from unittest.mock import Mock

from ...src.database import db
from ...src import create_app  # Update the import path
from ...src.models import Entity, LightState  # Update the import path
from ...src.endpoints.color import set_color  # Update the import path

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        app.strip = Mock()
        app.strip.numPixels.return_value = 100

        # Mock 'setPixelColor', 'setBrightness', and 'show' as needed
        # These might just be dummy methods that don't need to return anything
        app.strip.setPixelColor = Mock()
        app.strip.setBrightness = Mock()
        app.strip.show = Mock()


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
        return entity.id  # return only the id

@pytest.fixture
def set_color_url(app):
    with app.app_context():
        return url_for('color.set_color')

def test_set_color_valid(client, init_entity, app, set_color_url):
    with app.app_context():  # Use app_context to set up the Flask application context
        # Fetch the entity using the recommended method
        entity = db.session.get(Entity, init_entity)

        data = {
            'entity': entity.id,
            'red': 255,
            'green': 100,
            'blue': 50,
            'brightness': 100,
            'is_on': 'true'
        }
        response = client.post(set_color_url, data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert 'Color updated successfully' in response.json['success']



def test_set_color_missing_entity(client, app, set_color_url):
    with app.app_context():
        data = {
            'red': 255,
            'green': 100,
            'blue': 50,
            'brightness': 200,
            'is_on': 'true'
        }
        response = client.post(set_color_url, data=json.dumps(data), content_type='application/json')
        assert response.status_code == 400
        assert 'Missing entity' in response.json['error']

def test_set_color_entity_not_found(client, app, set_color_url):
    with app.app_context():
        data = {
            'entity': 999,  # Non-existent entity ID
            'red': 255,
            'green': 100,
            'blue': 50,
            'brightness': 200,
            'is_on': 'true'
        }
        response = client.post(set_color_url, data=json.dumps(data), content_type='application/json')
        assert response.status_code == 404
        assert 'Entity not found' in response.json['error']

