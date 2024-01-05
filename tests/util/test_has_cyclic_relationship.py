import pytest
from ...src import create_app
from ...src.database import db
from ...src.models import Entity
from ...src.util.has_cyclic_relationship import has_cyclic_relationship

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
def init_entities(app):
    with app.app_context():
        entity1 = Entity(id=1, name="Entity1", start_addr=1, end_addr=10, parent_id=None) #init_entities[0]
        entity2 = Entity(id=2, name="Entity2", start_addr=1, end_addr=10, parent_id=1) #init_entities[1]
        entity3 = Entity(id=3, name="Entity3", start_addr=1, end_addr=10, parent_id=2) #init_entities[2]
        db.session.add(entity1)
        db.session.add(entity2)
        db.session.add(entity3)
        db.session.commit()
        return [entity1.id, entity2.id, entity3.id]

def test_has_cyclic_relationship_no_cycle(app, init_entities):
    with app.app_context():
        assert not has_cyclic_relationship(init_entities[0], init_entities[1])
        assert not has_cyclic_relationship(init_entities[0], init_entities[2])
        assert not has_cyclic_relationship(init_entities[0], init_entities[2])

def test_has_cyclic_relationship_with_cycle(app, init_entities):
    with app.app_context():
        # Introduce a cycle
        entity1 = db.session.get(Entity, init_entities[0])
        entity1.parent_id = 3
        db.session.commit()

        assert has_cyclic_relationship(init_entities[0], init_entities[2])

def test_has_cyclic_relationship_same_entity(app, init_entities):
    with app.app_context():
        assert has_cyclic_relationship(init_entities[0], init_entities[0])
