import pytest
import json
from flask import url_for
from ...src import create_app, db
from ...src.models import Entity

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

def test_manage_entity_post(client):
    data = {
        'name': 'New Entity',
        'start_addr': 100,
        'end_addr': 200,
        'parent_id': None
    }
    response = client.post(url_for('manage_entity'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert 'Entity created successfully' in response.json['success']

def test_manage_entity_put(client):
    # First, create an entity
    entity = Entity(name="Existing Entity", start_addr=100, end_addr=200, parent_id=None)
    with app.app_context():
        db.session.add(entity)
        db.session.commit()
    
    # Then, update it
    data = {
        'id': entity.id,
        'name': 'Updated Entity',
        'start_addr': 150,
        'end_addr': 250,
        'parent_id': None
    }
    response = client.put(url_for('manage_entity'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert 'Entity updated successfully' in response.json['success']

def test_manage_entity_delete(client):
    # Create an entity to delete
    entity = Entity(name="Entity to Delete", start_addr=100, end_addr=200, parent_id=None)
    with app.app_context():
        db.session.add(entity)
        db.session.commit()

    # Delete the entity
    data = {'id': entity.id}
    response = client.delete(url_for('manage_entity'), data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert 'Entity deleted successfully' in response.json['success']

def test_manage_entity_get(client):
    # Create an entity to retrieve
    entity = Entity(name="Entity to Retrieve", start_addr=100, end_addr=200, parent_id=None)
    with app.app_context():
        db.session.add(entity)
        db.session.commit()

    # Retrieve the entity
    response = client.get(url_for('manage_entity', id=entity.id))
    assert response.status_code == 200
    # Add assertions to check the retrieved entity data

