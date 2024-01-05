import pytest
from unittest.mock import Mock, call
from src.endpoints.color import colorWipe

def test_colorWipe():
    # Create a mock strip object
    mock_strip = Mock()
    mock_strip.numPixels.return_value = 10  # Assuming the strip has 10 pixels

    # Define the parameters for the colorWipe function
    test_color = 123  # Example color
    test_brightness = 100
    range_start = 2
    range_end = 5
    wait_ms = 5

    # Call the function with the mock strip and other parameters
    colorWipe(mock_strip, test_color, test_brightness, range_start, range_end, wait_ms)

    # Define expected calls to the mock_strip
    expected_calls = [
        call.setPixelColor(2, test_color),
        call.setBrightness(test_brightness),
        call.show(),
        call.setPixelColor(3, test_color),
        call.setBrightness(test_brightness),
        call.show(),
        call.setPixelColor(4, test_color),
        call.setBrightness(test_brightness),
        call.show(),
        call.setPixelColor(5, test_color),
        call.setBrightness(test_brightness),
        call.show()
    ]

    # Check if the mock strip object was called as expected
    mock_strip.assert_has_calls(expected_calls, any_order=False)
