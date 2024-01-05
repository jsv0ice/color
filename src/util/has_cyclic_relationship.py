from ..models import Entity

def has_cyclic_relationship(start_id, current_id):
    """
    Checks for a cyclic relationship in the entity hierarchy.

    Parameters:
    start_id (int): The ID of the starting entity to check for cyclic relationships.
    current_id (int): The ID of the current entity in the hierarchy traversal.

    Returns:
    bool: True if a cyclic relationship is detected, False otherwise.
    """

    # If the start ID matches the current ID, a cycle is detected
    if start_id == current_id:
        return True

    # Fetch the current entity by its ID
    current_entity = Entity.query.filter_by(id=current_id).first()

    # If the current entity exists and has a parent, continue traversing the hierarchy
    if current_entity and current_entity.parent:
        return has_cyclic_relationship(start_id, current_entity.parent.id)

    # If no cycle is detected, return False
    return False