import pytest
from ...src import create_app, db
from ...src.models import Entity
from ...src.endpoints.entity import delete_entity

@pytest.fixture
def app():
    app = create_app() 
    with app.app_context():
        print('in app create:' + str(id(db.session)))
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
        entity = Entity(id=1, name="Entity to Delete", start_addr=100, end_addr=200, parent_id=None)
        db.session.add(entity)
        db.session.commit()
        print('in setup:' + str(id(db.session)))
        return entity.id

def test_delete_entity_valid(app, init_entity):
    with app.app_context():
        entity = db.session.get(Entity, init_entity)
        delete_data = {'id': entity.id}
        print('in test:' + str(id(db.session)))

        response = delete_entity(delete_data)
        
        assert response[1] == 200
        assert 'Entity deleted successfully' in response[0].json['success']
        db.session.expunge_all()
        deleted_entity = db.session.get(Entity, entity.id)
        assert deleted_entity is None

def test_delete_entity_not_found(app):
    with app.app_context():
        delete_data = {'id': 999}  # Non-existent entity ID
        response = delete_entity(delete_data)
        assert response[1] == 404
        assert 'Entity not found' in response[0].json['error']

def test_delete_entity_missing_data(app):
    with app.app_context():
        delete_data = {}  # Missing ID
        response = delete_entity(delete_data)
        assert response[1] == 400
        assert 'Missing data' in response[0].json['error']
