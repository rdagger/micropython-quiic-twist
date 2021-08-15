"""MicroPython Quiic Twist encoder I2C driver."""
from micropython import const  # type: ignore


class Encoder(object):
    """I2C interace for Spark Fun Quiic Twist RGB encoder."""

    # Command constants
    TWIST_ID = const(0x00)
    TWIST_STATUS = const(0x01)  # 0=encoder moved, 1=btn pressed, 2=btn clicked
    TWIST_VERSION = const(0x02)
    TWIST_ENABLE_INTS = const(0x04)  # 0=encoder interrupt, 1=button interrupt
    TWIST_COUNT = const(0x05)
    TWIST_DIFFERENCE = const(0x07)
    TWIST_LAST_ENCODER_EVENT = const(0x09)  # Ms since last movement of knob
    TWIST_LAST_BUTTON_EVENT = const(0x0B)  # Ms since last press/releas
    TWIST_RED = const(0x0D)
    TWIST_GREEN = const(0x0E)
    TWIST_BLUE = const(0x0F)
    TWIST_CONNECT_RED = const(0x10)  # Change red LED for each encoder tick
    TWIST_CONNECT_GREEN = const(0x12)  # Change green LED for each encoder tick
    TWIST_CONNECT_BLUE = const(0x14)  # Change blue LED for each encoder tick
    TWIST_TURN_INT_TIMEOUT = const(0x16)
    TWIST_CHANGE_ADDRESS = const(0x18)
    TWIST_LIMIT = const(0x19)

    STATUS_BUTTON_CLICKED = const(2)
    STATUS_BUTTON_PRESSED = const(1)
    STATUS_ENCODER_MOVED = const(0)
    ENABLE_INTERRUPT_BUTTON = const(1)
    ENABLE_INTERRUPT_ENCODER = const(0)

    def __init__(self, i2c, address=0x3F):
        """Constructor for encoder.

        Args:
            i2c (class): I2C bus
            address (int):  Encoder I2C address
        """
        self.address = address
        self.i2c = i2c
        self.reset_count()
        self.reset_status()
        self.reset_interrupts()
        self.set_limit(23)
        self.set_color(0, 0, 0)
        self.set_connect_color(0, 0, 0)

    def get_color(self):
        """Gets the current knob color.

        Returns:
            [byte, byte, byte]: Red ,Green ,Blue
        """
        red = self.read_byte(self.TWIST_RED)
        green = self.read_byte(self.TWIST_GREEN)
        blue = self.read_byte(self.TWIST_BLUE)
        return [red, green, blue]

    def get_connect_color(self):
        """Gets the relation between each color and the twisting of the knob.

        Returns:
            [int, int, int]: Red ,Green ,Blue
        """
        red = self.read_word(self.TWIST_CONNECT_RED)
        green = self.read_word(self.TWIST_CONNECT_GREEN)
        blue = self.read_word(self.TWIST_CONNECT_BLUE)
        return [red, green, blue]

    def get_count(self):
        """Returns the number of indents the user has twisted the knob.

        Notes:
            Looks like there's a bug in the firmware when turning the encoder
            counter-clockwise from the zero position.  It retuns a value that
            is 1 too high.
        """
        return self.read_word(self.TWIST_COUNT)

    def get_diff(self, clear=False):
        """Returns the number of ticks since last check.

        Args:
            clear (bool): True = clear the current value. Default is False.
        Returns:
            int: the difference
        """
        difference = self.read_word(self.TWIST_DIFFERENCE)

        if difference > 32767:
            difference = -(65536 - difference)  # Check for negative value

        if clear:
            self.write_word(self.TWIST_DIFFERENCE, 0)

        return difference

    def get_int_timeout(self):
        """Get number of milliseconds that elapse between end of knob
        turning and interrupt firing.

        Returns:
            int: milliseconds
        """
        return self.read_word(self.TWIST_TURN_INT_TIMEOUT)

    def get_limit(self):
        """Returns the limit of allowed counts before wrapping.

        Returns:
         int: The limit (0=disabled)
        """
        return self.read_word(self.TWIST_LIMIT)

    def get_time_since_last_move(self, clear=False):
        """Returns the number of milliseconds since the last encoder movement

        Args:
            clear (bool): True = clear value (False default)
        Returns:
            int: milliseconds (maximum 65,535 then rolls over)
        """
        time_elapsed = self.read_word(self.TWIST_LAST_ENCODER_EVENT)

        if clear:
            self.write_word(self.TWIST_LAST_ENCODER_EVENT, 0)

        return time_elapsed

    def get_time_since_last_press(self, clear=False):
        """Returns the number of milliseconds since the last button event.

        Args:
            clear (bool): True = clear value (default)
        Returns:
            int: milliseconds (maximum 65,535 then rolls over)
        Note:
            Not compatible with interrupts which requires
            button status bits to be reset (clearing timer)
        """
        time_elapsed = self.read_word(self.TWIST_LAST_BUTTON_EVENT)

        # Clear the current value if requested
        if clear:
            self.write_ind(self.TWIST_LAST_BUTTON_EVENT, 0)

        return time_elapsed

    def get_version(self):
        """Returns firmware version number.

        Returns:
            int: The firmware version
        """
        return self.read_word(self.TWIST_VERSION)

    version = property(get_version)

    def has_clicked(self):
        """Returns true if a click event has occurred."""
        status = self.read_byte(self.TWIST_STATUS)
        self.write_byte(self.TWIST_STATUS,
                        status & ~(1 << self.STATUS_BUTTON_CLICKED))
        return status >> self.STATUS_BUTTON_CLICKED & 1 != 0

    def has_moved(self):
        """Returns true if knob has been twisted."""
        status = self.read_byte(self.TWIST_STATUS)
        self.write_byte(self.TWIST_STATUS,
                        status & ~(1 << self.STATUS_ENCODER_MOVED))
        return status >> self.STATUS_ENCODER_MOVED & 1 != 0

    def is_pressed(self):
        """Returns true if button is currently being pressed."""
        status = self.read_byte(self.TWIST_STATUS)
        self.write_byte(self.TWIST_STATUS,
                        status & ~(1 << self.STATUS_BUTTON_PRESSED))
        return status >> self.STATUS_BUTTON_PRESSED & 1 != 0

    def reset_count(self):
        """Reset the encoder count and difference to zero."""

        self.write_word(self.TWIST_COUNT, 0)
        self.write_word(self.TWIST_DIFFERENCE, 0)

    def reset_interrupts(self):
        """Clears the interrupt bits"""
        status = self.read_byte(self.TWIST_STATUS)
        self.write_byte(self.TWIST_STATUS, status & 0b11111100)

    def reset_status(self):
        """Clears the button status clicked and is_pressed bits"""
        status = self.read_byte(self.TWIST_STATUS)
        self.write_byte(self.TWIST_STATUS, status & 0b11110011)

    def reset_timers(self):
        """Reset button and encoder interval timers."""
        self.write_word(self.TWIST_LAST_ENCODER_EVENT, 0)
        self.write_word(self.TWIST_LAST_BUTTON_EVENT, 0)

    def set_color(self, red, green, blue):
        """Sets the color of the encoder RGB LED.

        Args:
            red (int): Red component
            green (int): Green component
            blue (int): Blue component
        """
        self.write_list(self.TWIST_RED, [red, green, blue])

    def set_connect_color(self, red, green, blue):
        """Sets the relation between each color and the twisting of the knob.
            Connect the LED so it changes with each encoder tick.
            Negative numbers are allowed.
            (so LED can vary automatically while encoder is turned)
            red (int): Red component
            green (int): Green component
            blue (int): Blue component
        """
        colors = red.to_bytes(2, 'little', True) + \
            green.to_bytes(2, 'little', True) + \
            blue.to_bytes(2, 'little', True)
        self.write_bytes(self.TWIST_CONNECT_RED, colors)

    def set_count(self, count):
        """
            Set the encoder count to a specific amount.
        Args:
            count (int): Amount to set encoder count.
        """
        self.write_word(self.TWIST_COUNT, count)

    def set_interrupts(self, button, encoder):
        """Enable or disable interrupts for button and encoder.

        Args:
            button (bool): True=enable button interrupt, False=disable
            encoder (bool): True=enable encoder interrupt, False=disable
        """
        ints = 0
        if button:
            ints |= 1 << self.ENABLE_INTERRUPT_BUTTON
        if encoder:
            ints |= 1 << self.ENABLE_INTERRUPT_ENCODER
        self.write_byte(self.TWIST_ENABLE_INTS, ints)

    def set_int_timeout(self, timeout):
        """Set number of milliseconds that elapse between end of knob
        turning and interrupt firing.

        Args:
            timeout (int): The timeout value in milliseconds.
        """
        self.write_word(self.TWIST_TURN_INT_TIMEOUT, timeout)

    def set_limit(self, steps):
        """Set the encoder indent count limit (steps per rotation).

        Args:
            steps (int): The value to set the limit (0=disabled).
        """
        self.write_word(self.TWIST_LIMIT, steps)

    def read_byte(self, cmd):
        """Read byte from encoder.

        Args:
            cmd (byte): Command address to read
        """
        buf = self.i2c.readfrom_mem(self.address, cmd, 1)
        return int.from_bytes(buf, 'little')

    def read_word(self, cmd):
        """Read double byte from encoder.

        Args:
            cmd (byte): Command address to read
        Returns:
            int: value
        """
        buf = self.i2c.readfrom_mem(self.address, cmd, 2)
        return int.from_bytes(buf, 'little', True)

    def write_byte(self, cmd, data):
        """Write byte to encoder.

        Args:
            cmd (byte): Command address to write
            data (byte): Byte to write
        """
        self.i2c.writeto_mem(self.address, cmd, bytearray([data]))

    def write_bytes(self, cmd, data):
        """Write bytes to encoder.

        Args:
            cmd (byte): Command address to write
            data (bytes): Bytes to write
        """
        self.i2c.writeto_mem(self.address, cmd, data)

    def write_word(self, cmd, data):
        """Write double byte to encoder.

        Args:
            cmd (byte): Command address to write
            data (int): Int to write
        """
        self.i2c.writeto_mem(self.address,
                             cmd,
                             data.to_bytes(2, 'little'))

    def write_list(self, cmd, data):
        """Write list of bytes to encoder.

        Args:
            cmd (byte): Command address to write
            data (list): List to write
        """
        self.i2c.writeto_mem(self.address, cmd, bytearray(data))
