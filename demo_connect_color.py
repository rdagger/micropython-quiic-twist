"""Quiic Twist encoder demo (connect color)."""
from time import sleep
from machine import I2C, Pin  # type: ignore
from quiic_twist import Encoder
"""
ESP32 has default pins for the hardware I2C buses, but you can use other pins.
It is not necessary to specify the pins if you use the defaults:
I2C Bus | SCL | SDA |
   # 0  | 18  | 19  |
   # 1  | 25  | 26  |
Raspberry Pi Pico does not have defaults. Pins must be specified from:
I2C Bus # 0-SDA -> GPO/GP4/GP8/GPl2/GP16/GP20
I2C Bus # 0-SCL -> GP1/GP5/GP9/GPl3/GP17/GP21
I2C Bus # 1-SDA -> GP2/GP6/GP10/GP14/GP18/GP26
I2C Bus # 1-SCL -> GP3/GP7/GP11/GP15/GP19/GP27
"""
i2c = I2C(1, freq=400000, scl=Pin(3), sda=Pin(2))  # Pico I2C bus 1
encoder = Encoder(i2c)


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
