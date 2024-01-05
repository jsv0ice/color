import pytest
import json
from flask import url_for
from ...src import create_app
from ...src.database import db
from ...src.models import Entity

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

def test_manage_entity_post(client, app):
    with app.app_context():
        data = {
            'name': 'New Entity',
            'start_addr': 100,
            'end_addr': 200,
            'parent_id': None
        }
        response = client.post(url_for('entity.manage_entity'), data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert 'Entity created successfully' in response.json['success']

def test_manage_entity_put(client, app):
    # First, create an entity
    with app.app_context():
        entity = Entity(name="Existing Entity", start_addr=100, end_addr=200, parent_id=None)
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
        response = client.put(url_for('entity.manage_entity'), data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert 'Entity updated successfully' in response.json['success']

def test_manage_entity_delete(client, app):
    # Create an entity to delete
    
    with app.app_context():
        entity = Entity(name="Entity to Delete", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()

        # Delete the entity
        data = {'id': entity.id}
        response = client.delete(url_for('entity.manage_entity'), data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert 'Entity deleted successfully' in response.json['success']

def test_manage_entity_get_list(client, app):
    # Create an entity to retrieve
    
    with app.app_context():
        entity = Entity(name="Entity to Retrieve", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()

        # Retrieve the entity
        response = client.get(url_for('entity.manage_entity'))
        assert response.status_code == 200
        # Add assertions to check the retrieved entity data

def test_manage_entity_get(client, app):
    # Create an entity to retrieve
    
    with app.app_context():
        entity = Entity(name="Entity to Retrieve", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()

        # Retrieve the entity
        response = client.get(url_for('entity.manage_entity', body={"id": entity.id}))
        assert response.status_code == 200
        # Add assertions to check the retrieved entity data