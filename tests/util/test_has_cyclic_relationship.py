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
        entity4 = Entity(id=4, name="Entity4", start_addr=1, end_addr=10, parent_id=4) #init_entities[3]
        db.session.add(entity1)
        db.session.add(entity2)
        db.session.add(entity3)
        db.session.add(entity4)
        db.session.commit()
        return [entity1.id, entity2.id, entity3.id, entity4.id]

def test_has_cyclic_relationship_no_cycle(app, init_entities):
    with app.app_context():
        assert not has_cyclic_relationship(init_entities[1], init_entities[0], is_first_call=True)
        assert not has_cyclic_relationship(init_entities[2], init_entities[0], is_first_call=True)

def test_has_cyclic_relationship_with_cycle(app, init_entities):
    with app.app_context():
        # Introduce a cycle
        entity1 = db.session.get(Entity, init_entities[0])
        entity1.parent_id = 3
        db.session.commit()

        assert has_cyclic_relationship(init_entities[0], init_entities[2], is_first_call=True)

def test_has_cyclic_relationship_same_entity(app, init_entities):
    with app.app_context():
        entity = db.session.get(Entity, init_entities[3])
        assert has_cyclic_relationship(entity.id, entity.id, is_first_call=True)

def test_has_cyclic_relationship_with_none_parent(app, init_entities):
    with app.app_context():
        # Create an entity with no parent
        orphan_entity = Entity(id=5, name="Orphan", start_addr=11, end_addr=20, parent_id=None)
        db.session.add(orphan_entity)
        db.session.commit()

        # Test the function with an entity that has a None parent
        assert not has_cyclic_relationship(orphan_entity.id, init_entities[0], is_first_call=True)
