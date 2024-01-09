def validate_color_values(red, green, blue, brightness):
    """
    Validate the color and brightness values for the LED settings.

    Parameters:
    red (int): The red component of the color (0-255).
    green (int): The green component of the color (0-255).
    blue (int): The blue component of the color (0-255).
    brightness (int): The brightness level of the color (1-255).

    Returns:
    tuple: A tuple containing a boolean indicating validation success and an error message if any.
    """

    # Check if all values are integers
    if not all(isinstance(v, int) for v in [red, green, blue, brightness]):
        return False, "All values must be integers"

    # Check if RGB values are within the permissible range (0-255)
    if not all(0 <= v <= 255 for v in [red, green, blue]):
        return False, "Red, Green, Blue values must be between 0 and 255"

    # Check if brightness is within the permissible range (1-255)
    if not 0 <= brightness <= 100:
        return False, "Brightness must be between 0 and 100"

    # If all checks pass, return True with an empty error message
    return True, ""