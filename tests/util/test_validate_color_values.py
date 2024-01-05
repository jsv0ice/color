import pytest
from ...src.util.validate_color_values import validate_color_values  # Replace 'your_module' with the actual module name

def test_validate_color_values_valid():
    assert validate_color_values(255, 100, 50, 100) == (True, "")

def test_validate_color_values_invalid_rgb():
    assert validate_color_values(256, 100, 50, 200)[0] == False
    assert validate_color_values(255, -1, 50, 200)[0] == False
    assert validate_color_values(255, 100, 300, 200)[0] == False

def test_validate_color_values_invalid_brightness():
    assert validate_color_values(255, 100, 50, 0)[0] == False
    assert validate_color_values(255, 100, 50, 256)[0] == False

def test_validate_color_values_non_integer():
    assert validate_color_values("255", 100, 50, 200)[0] == False
    assert validate_color_values(255, 100.5, 50, 200)[0] == False
    assert validate_color_values(255, 100, [50], 200)[0] == False
    assert validate_color_values(255, 100, 50, "200")[0] == False
