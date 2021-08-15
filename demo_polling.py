"""Quiic Twist encoder demo (polling)."""
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
encoder.set_limit(12)  # Set count limit to 12 detents


def test():
    """Test code."""

    # Set the knob color to cyan
    encoder.set_color(0, 255, 255)

    version = encoder.get_version()
    print("Firmware version: {}".format(version))
    print("Limit: {}".format(encoder.get_limit()))

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
