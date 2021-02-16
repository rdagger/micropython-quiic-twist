"""Quiic Twist encoder demo (polling)."""
from time import sleep
from machine import Pin
from quiic_twist import Encoder

encoder = Encoder(scl=Pin(22), sda=Pin(21))


def test():
    """Test code."""

    # Set the knob color to cyan
    encoder.set_color(0, 255, 255)

    version = encoder.get_version()
    print("Firmware version: {0}".format(version))

    try:
        while True:
            clicked = encoder.has_clicked()
            moved = encoder.has_moved()
            if moved or clicked:
                count = encoder.get_count()
                diff = encoder.get_diff(True)
                is_pressed = encoder.is_pressed()
                print()
                print("Encoder moved: {}, Button clicked: {}".format(moved,
                                                                     clicked))
                print("Tick count: {}, Difference: {}".format(count,
                                                              diff))
                print("Button is pressed: {}".format(is_pressed))
            sleep(.3)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed to exit.")
    finally:
        encoder.set_color(0, 0, 0)


test()
