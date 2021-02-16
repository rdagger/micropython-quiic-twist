"""Quiic Twist encoder demo (connect color)."""
from time import sleep
from machine import Pin
from quiic_twist import Encoder

encoder = Encoder(scl=Pin(22), sda=Pin(21))


def print_colors():
    """Print current RGB colors."""
    colors = encoder.get_color()
    print("Red {0:03d} | Green {1:03d} | Blue {2:03d}".format(*colors))


def test():
    """Test code."""
    encoder.set_color(125, 0, 125)  # Set red & blue LED to ~1/2 max brightness
    encoder.set_connect_color(-5,  # Decrement red brightness 5 with each tick
                              0,
                              5)  # Increment blue brightness 5 with each tick

    print_colors()

    try:
        while True:
            if encoder.has_clicked():
                encoder.set_color(125, 0, 125)  # Reset color if button pressed
                print_colors()
            if encoder.has_moved():
                print_colors()
            sleep(.3)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed to exit.")
    finally:
        encoder.set_color(0, 0, 0)


test()
