from ..models import Entity
from flask import current_app

def has_cyclic_relationship(start_id, current_id, is_first_call=True):
    """
    Checks for a cyclic relationship in the entity hierarchy.

    Parameters:
    start_id (int): The ID of the starting entity to check for cyclic relationships.
    current_id (int): The ID of the current entity in the hierarchy traversal.

    Returns:
    bool: True if a cyclic relationship is detected, False otherwise.
    """
    print(start_id, current_id, is_first_call)
    is_cycle = False
    # If it's not the first call and the start ID matches the current ID, a cycle is detected
    start_entity = Entity.query.filter_by(id=start_id).first()
    
    # Fetch the current entity by its ID
    current_entity = Entity.query.filter_by(id=current_id).first()

    print('start_entity, current_entity, current_entity.parent_id')
    print(start_entity.id, current_entity.id, current_entity.parent_id)

    if current_entity.parent_id is None:
        return False
    
    if current_entity.parent_id == current_entity.id:
        return True
   
    if current_entity.parent_id == start_entity.id:
        return True

    # Continue traversing the hierarchy
    if is_cycle is False:
        return has_cyclic_relationship(start_id, current_entity.parent_id, is_first_call=False)
