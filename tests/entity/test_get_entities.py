import pytest
from flask import jsonify
from ...src import create_app, db
from ...src.models import Entity, LightState
from ...src.endpoints.entity import get_entities

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
def init_entities(app):
    with app.app_context():
        entity1 = Entity(id=1, name="Entity1", start_addr=100, end_addr=200, parent_id=None)
        entity2 = Entity(id=2, name="Entity2", start_addr=300, end_addr=400, parent_id=1)
        state1 = LightState(entity_id=1, is_on=True, red=255, green=255, blue=255, brightness=100)
        state2 = LightState(entity_id=2, is_on=False, red=0, green=0, blue=0, brightness=0)
        db.session.add(entity1)
        db.session.add(entity2)
        db.session.add(state1)
        db.session.add(state2)
        db.session.commit()

def test_get_entities(app, init_entities):
    with app.app_context():
        response = get_entities()
        assert response[1] == 200
        entities_data = response[0].json
        assert len(entities_data) == 2

        # Test the first entity data
        assert entities_data[0]['id'] == 1
        assert entities_data[0]['name'] == "Entity1"
        assert entities_data[0]['state']['is_on'] == True

        # Test the second entity data
        assert entities_data[1]['id'] == 2
        assert entities_data[1]['name'] == "Entity2"
        assert entities_data[1]['state']['is_on'] == False

def test_get_entities_no_entities(app):
    with app.app_context():
        response = get_entities()
        assert response[1] == 200
        entities_data = response[0].json
        assert len(entities_data) == 0