"""Quiic Twist encoder demo (Interrupts).

Notes:
    The interrupt functionality on the SparkFun encoder board
    is poorly implemented.  Their Atmel Tiny84A code is buggy.
    I've made notes throughout the demo where workarounds
    are required.
"""
from time import sleep
from random import randint
from machine import I2C, idle, Pin  # type: ignore
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

encoder.set_interrupts(True, True)
print("Interrupt timeout: {}ms".format(encoder.get_int_timeout()))


def int_press(pin):
    """Callback fires when encoder turned or pressed."""
    print("\nInterrupt fired.")
    if encoder.has_moved():
        count = encoder.get_count()
        diff = encoder.get_diff(True)
        print("Tick count: {}, Difference: {}".format(count, diff))

    # NOTE: Must wait for button to be released before checking button
    button_pressed = False
    while encoder.is_pressed():
        button_pressed = True
        idle()
    # BUG: has_clicked does not always register on interrupts
    # Added button_pressed boolean for better reliability
    if button_pressed or encoder.has_clicked():
        print("Button pressed.")
        encoder.set_color(randint(0, 256), randint(0, 256), randint(0, 256))
    # NOTE: Must manually clear button_clicked status or interrupt freezes low
    # Unfortunately clearing the status bits resets the button interval timer
    # Button must also be released before clearing (see note above)
    encoder.reset_status()


def test():
    """Test code."""

    int_pin = Pin(18, Pin.IN, pull=None)
    int_pin.irq(trigger=int_pin.IRQ_FALLING,
                handler=int_press)

    # Set the knob color to cyan
    encoder.set_color(255, 255, 0)

    encoder.reset_timers()
    counter = 0
    try:
        while True:
            counter += 1
            if counter == 10:
                # Print interval since last movement every 10 seconds
                interval = encoder.get_time_since_last_move() / 1000
                print("\nLast movement {:.1f} seconds ago.".format(interval))
                # NOTE: button interval tracking does not work with interrupts
                counter = 0
            sleep(1)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed to exit.")
    finally:
        encoder.set_color(0, 0, 0)


test()
