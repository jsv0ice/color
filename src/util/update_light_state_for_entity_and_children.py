from ..models import Entity, LightState
from .. import db

def update_light_state_for_entity_and_children(entity_id, red, green, blue, brightness, is_on):
    """
    Recursively updates the light state for a given entity and all its child entities.

    Parameters:
    entity_id (int): The ID of the entity whose light state is to be updated.
    red (int): The red component of the color (0-255).
    green (int): The green component of the color (0-255).
    blue (int): The blue component of the color (0-255).
    brightness (int): The brightness level of the color (1-255).
    is_on (bool): The state of the light (True for on, False for off).

    Returns:
    None
    """

    # Fetch the entity by its ID
    entity = Entity.query.filter_by(id=entity_id).first()
    if not entity:
        return

    # Update the light state of the current entity
    current_state = LightState.query.filter_by(entity_id=entity.id).order_by(LightState.timestamp.desc()).first()
    if not current_state or any([current_state.is_on != is_on,
                                 current_state.red != red,
                                 current_state.green != green,
                                 current_state.blue != blue,
                                 current_state.brightness != int(brightness/2.55)]):
        new_state = LightState(entity_id=entity.id, is_on=is_on, red=red, green=green, blue=blue, brightness=int(brightness/2.55))
        db.session.add(new_state)

    # Recursively update the light state of all child entities
    for child in entity.children:
        update_light_state_for_entity_and_children(child.id, red, green, blue, brightness, is_on)