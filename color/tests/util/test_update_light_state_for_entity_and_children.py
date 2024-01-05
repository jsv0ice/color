import pytest
from src import create_app, db
from src.models import Entity, LightState
from src.util.update_light_state_for_entity_and_children import update_light_state_for_entity_and_children

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
def init_entity_hierarchy(app):
    with app.app_context():
        parent = Entity(id=1, name="Parent", start_addr=100, end_addr=200, parent_id=None)
        child = Entity(id=2, name="Child", start_addr=300, end_addr=400, parent_id=1)
        db.session.add(parent)
        db.session.add(child)
        db.session.commit()

def test_update_light_state_for_entity_and_children(app, init_entity_hierarchy):
    with app.app_context():
        # Update light state for parent and its children
        update_light_state_for_entity_and_children(1, 255, 255, 255, 255, True)
        db.session.commit()

        # Check updated state for parent
        parent_state = LightState.query.filter_by(entity_id=1).order_by(LightState.timestamp.desc()).first()
        assert parent_state.is_on == True
        assert parent_state.red == 255
        assert parent_state.green == 255
        assert parent_state.blue == 255
        assert parent_state.brightness == int(255/2.55)

        # Check updated state for child
        child_state = LightState.query.filter_by(entity_id=2).order_by(LightState.timestamp.desc()).first()
        assert child_state.is_on == True
        assert child_state.red == 255
        assert child_state.green == 255
        assert child_state.blue == 255
        assert child_state.brightness == int(255/2.55)

# Replace 'your_application' and 'your_module' with the actual names used in your project.
