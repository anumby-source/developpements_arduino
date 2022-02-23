# SevSeg Library
#
# Copyright 2020 Dean Reading
#
# This library allows an Arduino to easily display numbers and letters on a
# 7-segment display without a separate 7-segment display controller.
#
# See the included readme for instructions.
# https://github.com/DeanIsMe/SevSeg
#

import time
from GS_timing import micros

# ARDUINO =================================================
def digitalWrite(pin, value):
    print("ARDUINO> digitalWrite pin=", pin, "value=", value)


def delayMicroseconds(micros):
    pass


"""
def micros() -> int:
    time.
"""

def pinMode(pin, mode):
    print("ARDUINO> pinMode pin=", pin, "mode=", mode)


def constrain(x, a, b) -> int:
    if x < a:
        return a
    if x > b:
        return b
    return x


def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


LOW = 0
HIGH = 1
OUTPUT = 1
# ==========================================================

# Can be increased, but the max number is 2^31
MAXNUMDIGITS = 8

# if defined(ARDUINO) && ARDUINO >= 100
# include "Arduino.h"
# else
# include "WProgram.h"
# endif

# Use defines to link the hardware configurations to the correct numbers
COMMON_CATHODE = 0
COMMON_ANODE = 1
N_TRANSISTORS = 2
P_TRANSISTORS = 3
NP_COMMON_CATHODE = 1
NP_COMMON_ANODE = 0

# Must match with 'digit_code_map'
BLANK_IDX = 36
DASH_IDX = 37
PERIOD_IDX = 38
ASTERISK_IDX = 39
UNDERSCORE_IDX = 40

powers_of_10 = [
  1,
  10,
  100,
  1000,
  10000,
  100000,
  1000000,
  10000000,
  100000000,
  1000000000]


powers_of_16 = [
  0x1,
  0x10,
  0x100,
  0x1000,
  0x10000,
  0x100000,
  0x1000000,
  0x10000000]
# 16^7


# digit_code_map indicate which segments must be illuminated to display
# each number.
digit_code_map = [
  # GFEDCBA  Segments      7-segment map:
  0b00111111,  # 0   "0"          AAA
  0b00000110,  # 1   "1"         F   B
  0b01011011,  # 2   "2"         F   B
  0b01001111,  # 3   "3"          GGG
  0b01100110,  # 4   "4"         E   C
  0b01101101,  # 5   "5"         E   C
  0b01111101,  # 6   "6"          DDD
  0b00000111,  # 7   "7"
  0b01111111,  # 8   "8"
  0b01101111,  # 9   "9"
  0b01110111,  # 65  'A'
  0b01111100,  # 66  'b'
  0b00111001,  # 67  'C'
  0b01011110,  # 68  'd'
  0b01111001,  # 69  'E'
  0b01110001,  # 70  'F'
  0b00111101,  # 71  'G'
  0b01110110,  # 72  'H'
  0b00110000,  # 73  'I'
  0b00001110,  # 74  'J'
  0b01110110,  # 75  'K'  Same as 'H'
  0b00111000,  # 76  'L'
  0b00000000,  # 77  'M'  NO DISPLAY
  0b01010100,  # 78  'n'
  0b00111111,  # 79  'O'
  0b01110011,  # 80  'P'
  0b01100111,  # 81  'q'
  0b01010000,  # 82  'r'
  0b01101101,  # 83  'S'
  0b01111000,  # 84  't'
  0b00111110,  # 85  'U'
  0b00111110,  # 86  'V'  Same as 'U'
  0b00000000,  # 87  'W'  NO DISPLAY
  0b01110110,  # 88  'X'  Same as 'H'
  0b01101110,  # 89  'y'
  0b01011011,  # 90  'Z'  Same as '2'
  0b00000000,  # 32  ' '  BLANK
  0b01000000,  # 45  '-'  DASH
  0b10000000,  # 46  '.'  PERIOD
  0b01100011,  # 42 '*'  DEGREE ..
  0b00001000,  # 95 '_'  UNDERSCORE
]

# Constant pointers to constant data
numeral_codes = digit_code_map
alpha_codes = digit_code_map[10]


class SevSeg:
    digit_on_val = 0
    digit_off_val = 0
    segment_on_val = 0
    segment_off_val = 0
    res_on_segments = 0
    update_with_delays = 0
    leading_zeros = 0
    digit_pins = []
    segment_pins = []
    num_digits = 0
    num_segments = 0
    prev_update_idx = 0          # The previously updated segment or digit
    digit_codes = []            # The active setting of each segment of each digit MAXNUMDIGITS
    prev_update_time = 0         # The time (millis()) when the display was last updated
    led_on_time = 0              # The time (us) to wait with LEDs on
    wait_off_time = 0            # The time (us) to wait with LEDs off
    wait_off_active = 0          # Whether  the program is waiting with LEDs off

    def __init__(self):
        # Initial value
        self.led_on_time = 2000  # Corresponds to a brightness of 100
        self.wait_off_time = 0
        self.wait_off_active = False
        self.num_digits = 0
        self.prev_update_idx = 0
        self.prev_update_time = 0
        self.update_with_delays = 0

    # segment_off
    #
    # Turns a segment off, as well as all digit pins
    def segment_off(self, segment_num):
        for digit_num in range(self.num_digits):
            digitalWrite(self.digit_pins[digit_num], self.digit_off_val)

        digitalWrite(self.segment_pins[segment_num], self.segment_off_val)

    # segment_on
    #
    # Turns a segment on, as well as all corresponding digit pins
    # (according to digit_codes[])
    def segment_on(self, segment_num):
        digitalWrite(self.segment_pins[segment_num], self.segment_on_val)

        for digit_num in range(self.num_digits):
            if self.digit_codes[digit_num] & (1 << segment_num):
                # Check a single bit
                digitalWrite(self.digit_pins[digit_num], self.digit_on_val)

    # digit_on
    #
    # Turns a digit on, as well as all corresponding segment pins
    # (according to digit_codes[])
    def digit_on(self, digit_num):
        digitalWrite(self.digit_pins[digit_num], self.digit_on_val)
        for segment_num in range(self.num_segments):
            if self.digit_codes[digit_num] & (1 << segment_num):
                # Check a single bit
                digitalWrite(self.segment_pins[segment_num], self.segment_on_val)

    # digit_off
    #
    # Turns digit off, as well as all segment pins
    def digit_off(self, digit_num):
        for segment_num in range(self.num_segments):
            digitalWrite(self.segment_pins[segment_num], self.segment_off_val)
        digitalWrite(self.digit_pins[digit_num], self.digit_off_val)

    def a(self):
        # RESISTORS ON DIGITS, UPDATE WITHOUT DELAYS
        if self.wait_off_active:
            self.wait_off_active = False
        else:
            # Turn all lights off for the previous segment
            self.segment_off(self.prev_update_idx)

            if self.wait_off_time:
                # Wait a delay with all lights off
                self.wait_off_active = True
                return

        self.prev_update_idx += 1
        if self.prev_update_idx >= self.num_segments:
            self.prev_update_idx = 0

        # Illuminate the required digits for the new segment
        self.segment_on(self.prev_update_idx)

    def b(self):
        # RESISTORS ON SEGMENTS, UPDATE WITHOUT DELAYS

        if self.wait_off_active:
            self.wait_off_active = False
        else:
            # Turn all lights off for the previous digit
            self.digit_off(self.prev_update_idx)

            if self.wait_off_time:
                # Wait a delay with all lights off
                self.wait_off_active = True
                return

        self.prev_update_idx += 1
        if self.prev_update_idx >= self.num_digits:
            self.prev_update_idx = 0

        # Illuminate the required segments for the new digit
        self.digit_on(self.prev_update_idx)

    def c(self):
        # RESISTORS ON DIGITS, UPDATE WITH DELAYS
        for segment_num in range(self.num_segments):
            # Illuminate the required digits for this segment
            self.segment_on(segment_num)

            # Wait with lights on (to increase brightness)
            delayMicroseconds(self.led_on_time)

            # Turn all lights off
            self.segment_off(segment_num)

            # Wait with all lights off if required
            if self.wait_off_time:
                delayMicroseconds(self.wait_off_time)

    def d(self):
        # RESISTORS ON SEGMENTS, UPDATE WITH DELAYS
        for digit_num in range(self.num_digits):
            # Illuminate the required segments for this digit
            self.digit_on(digit_num)

            # Wait with lights on (to increase brightness)
            delayMicroseconds(self.led_on_time)

            # Turn all lights off
            self.digit_off(digit_num)

            # Wait with all lights off if required
            if self.wait_off_time:
                delayMicroseconds(self.wait_off_time)

    def refresh_display(self):
        # refresh_display
        #
        # Turns on the segments specified in 'digit_codes[]'
        # There are 4 versions of this function, with the choice depending on the
        # location of the current-limiting resistors, and whether or not you wish to
        # use 'update delays' (the standard method until 2017).
        # For resistors on *digits* we will cycle through all 8 segments (7 + period),
        #    turning on the *digits* as appropriate for a given segment, before moving on
        #    to the next segment.
        # For resistors on *segments* we will cycle through all __ # of digits,
        #    turning on the *segments* as appropriate for a given digit, before moving on
        #    to the next digit.
        # If using update delays, refresh_display has a delay between each digit/segment
        #    as it cycles through. It exits with all LEDs off.
        # If not using updateDelays, refresh_display exits with a single digit/segment
        #    on. It will move to the next digit/segment after being called again (if
        #    enough time has passed).

        if not self.update_with_delays:
            us = micros()

            # Exit if it's not time for the next display change
            if self.wait_off_active:
                if (us - self.prev_update_time) < self.wait_off_time:
                    return
            else:
                if (us - self.prev_update_time) < self.led_on_time:
                    return

            self.prev_update_time = us

            if not self.res_on_segments:
                self.a()
            else:
                self.b()
        else:
            if not self.res_on_segments:
                self.c()
            else:
                self.d()

    # blank
    #
    def blank(self):
        for digit_num in range(self.num_digits):
            self.digit_codes = []
            self.digit_codes.append(digit_code_map[BLANK_IDX])

        self.segment_off(0)
        self.digit_off(0)

    # begin
    #
    # Saves the input pin numbers to the class and sets up the pins to be used.
    # If you use current-limiting resistors on your segment pins instead of the
    # digit pins, then set res_on_segments as true.
    # Set update_with_delays to true if you want to use the 'pre-2017' update method
    # In that case, the processor is occupied with delay functions while refreshing
    # leading_zeros_in indicates whether leading zeros should be displayed
    # disable_dec_point is true when the decimal point segment is not connected, in
    # which case there are only 7 segments.
    def begin(self,
              refresh_display,
              num_digits_in,
              digit_pins_in,
              segment_pins_in,
              res_on_segments_in=0,
              update_with_delays_in=0,
              leading_zeros_in=0,
              disable_dec_point=0):
        self.res_on_segments = res_on_segments_in
        self.update_with_delays = update_with_delays_in
        self.leading_zeros = leading_zeros_in

        self.num_digits = num_digits_in
        if disable_dec_point:
            self.num_segments = 7
        else:
            self.num_segments = 8

        # Limit the max number of digits to prevent overflowing
        if self.num_digits > MAXNUMDIGITS:
            self.num_digits = MAXNUMDIGITS

        if refresh_display == 0:
            # Common cathode
            self.digit_on_val = LOW
            self.segment_on_val = HIGH
        elif refresh_display == 1:
            # Common anode
            self.digit_on_val = HIGH
            self.segment_on_val = LOW
        elif refresh_display == 2:
            # With active-high, low-side switches (most commonly N-type FETs)
            self.digit_on_val = HIGH
            self.segment_on_val = HIGH
        elif refresh_display == 3:
            # With active low, high side switches (most commonly P-type FETs)
            self.digit_on_val = LOW
            self.segment_on_val = LOW

        # define the Off-Values depending on the On-Values
        if self.digit_on_val == HIGH:
            self.digit_off_val = LOW
        else:
            self.digit_off_val = HIGH

        # define the Off-Values depending on the On-Values
        if self.segment_on_val == HIGH:
            self.segment_off_val = LOW
        else:
            self.segment_off_val = HIGH

        # Save the input pin numbers to library variables
        for segment_num in range(self.num_segments):
            self.segment_pins.append(segment_pins_in[segment_num])

        for digit_num in range(self.num_digits):
            self.digit_pins.append(digit_pins_in[digit_num])

        # Set the pins as outputs, and turn them off
        for digit in range(self.num_digits):
            pinMode(self.digit_pins[digit], OUTPUT)
            digitalWrite(self.digit_pins[digit], self.digit_off_val)

        for segment_num in range(self.num_segments):
            pinMode(self.segment_pins[segment_num], OUTPUT)
            digitalWrite(self.segment_pins[segment_num], self.segment_off_val)

        self.blank()  # Initialise the display

    # set_brightness
    #
    # Sets led_on_time according to the brightness given. Standard brightness range
    # is 0 to 100. Flickering is more likely at brightness > 100, and < -100.
    # A positive brightness introduces a delay while the LEDs are on, and a
    # negative brightness introduces a delay while the LEDs are off.
    def set_brightness(self, brightness):
        # A number from 0..100
        brightness = constrain(brightness, -200, 200)
        if brightness > 0:
            self.led_on_time = map(brightness, 0, 100, 1, 2000)
            self.wait_off_time = 0
            self.wait_off_active = False
        else:
            self.led_on_time = 0
            self.wait_off_time = map(brightness, 0, -100, 1, 2000)

    # find_digits
    #
    # Decides what each digit will display.
    # Enforces the upper and lower limits on the number to be displayed.
    # digits[] is an output
    def find_digits(self, num_to_show, dec_places, ishex, digits):
        # const int32_t * powers_of_base = ishex ? powers_of_16: powers_of_10;

        if ishex:
            powers_of_base = powers_of_16
        else:
            powers_of_base = powers_of_10

        max_num = powers_of_base[self.num_digits] - 1
        min_num = -(powers_of_base[self.num_digits - 1] - 1)

        # If the number is out of range, just display dashes
        if num_to_show > max_num or num_to_show < min_num:
            for digit_num in range(self.num_digits):
                digits[digit_num] = DASH_IDX
            return
        else:
            digit_num = 0

        # Convert all number to positive values
        if num_to_show < 0:
            digits[0] = DASH_IDX
            digit_num = 1  # Skip the first iteration
            num_to_show = -num_to_show

        # Find all digits for base's representation, starting with the most
        # significant digit
        for digit_num in range(digit_num, self.num_digits):
            factor = powers_of_base[self.num_digits - 1 - digit_num]
            digits[digit_num] = int(num_to_show / factor)
            num_to_show -= digits[digit_num] * factor

        # Find unnnecessary leading zeros and set them to BLANK
        if dec_places < 0:
            dec_places = 0

        if not self.leading_zeros:
            for digit_num in range(self.num_digits - 1 - dec_places):
                if digits[digit_num] == 0:
                    digits[digit_num] = BLANK_IDX
                elif digits[digit_num] <= 9:
                    # Exit once the first non-zero number is encountered
                    break

    # set_digit_codes
    #
    # Sets the 'digit_codes' that are required to display the input numbers
    def set_digit_codes(self, digits, dec_places):
        # Set the digitCode for each digit in the display
        self.digit_codes = []
        for digit_num in range(self.num_digits):
            self.digit_codes.append(digit_code_map[digits[digit_num]])
            # Set the decimal point segment
            if dec_places >= 0:
                if digit_num == (self.num_digits - 1 - dec_places):
                    self.digit_codes[digit_num] |= digit_code_map[PERIOD_IDX]

    # set_new_num
    #
    # Changes the number that will be displayed.
    def set_new_num(self, num_to_show, dec_places, ishex=0):
        digits = []
        for digit in range(MAXNUMDIGITS):
            digits.append(0)
        self.find_digits(num_to_show, dec_places, ishex, digits)
        self.set_digit_codes(digits, dec_places)

    # set_number
    #
    # Receives an integer and passes it to 'set_new_num'.
    def set_number(self, num_to_show, dec_places=-1, ishex=0):
        self.set_new_num(num_to_show, dec_places, ishex)

    # set_number_f
    #
    # Receives a float, prepares it, and passes it to 'set_new_num'.
    def set_number_f(self, num_to_show, dec_places=-1, ishex=0):
        dec_places_pos = constrain(dec_places, 0, MAXNUMDIGITS)
        if ishex:
            num_to_show = num_to_show * powers_of_16[dec_places_pos]
        else:
            num_to_show = num_to_show * powers_of_10[dec_places_pos]

        # Modify the number so that it is rounded to an integer correctly

        if num_to_show >= 0.0:
            num_to_show += 0.5
        else:
            num_to_show += -0.5
        self.set_new_num(num_to_show, dec_places, ishex)

    # set_segments
    #
    # Sets the 'digit_codes' that are required to display the desired segments.
    # Using this function, one can display any arbitrary set of segments (like
    # letters, symbols or animated cursors). See set_digit_codes() for common
    # numeric examples.
    #
    # Bit-segment mapping:  0bHGFEDCBA
    #      Visual mapping:
    #                        AAAA          0000
    #                       F    B        5    1
    #                       F    B        5    1
    #                        GGGG          6666
    #                       E    C        4    2
    #                       E    C        4    2        (Segment H is often called
    #                        DDDD  H       3333  7      DP, for Decimal Point)
    def set_segments(self, segs):
        for digit in range(self.num_digits):
            self.digit_codes[digit] = segs[digit]

    # get_segments
    #
    # Gets the 'digit_codes' of currently displayed segments.
    # Using this function, one can get the current set of segments (placed
    # elsewhere) and manipulate them to obtain effects, for example blink of
    # only some digits.
    # See set_segments() for bit-segment mapping
    #
    def get_segments(self, segs):
        for digit in range(self.num_digits):
            segs[digit] = self.digit_codes[digit]

    # set_segments_digit
    #
    # Like set_segments above, but only manipulates the segments for one digit
    # digit_num is 0-indexed.
    def set_segments_digit(self, digit_num, segs):
        if digit_num < self.num_digits:
            self.digit_codes[digit_num] = segs

    # set_chars
    #
    # Displays the string on the display, as best as possible.
    # Only alphanumeric characters plus '-' and ' ' are supported
    def set_chars(self, str_value):
        for digit in range(self.num_digits):
            self.digit_codes[digit] = 0

        str_idx = 0  # Current position within str_value[]
        for digit_num in range(self.num_digits):
            ch = str_value[str_idx]
            if ch == '\0':
                break  # NULL string terminator
            if (ch >= '0') and (ch <= '9'):
                # Numerical
                self.digit_codes[digit_num] = numeral_codes[ch - '0']
            elif (ch >= 'A') and (ch <= 'Z'):
                self.digit_codes[digit_num] = alpha_codes[ch - 'A']
            elif (ch >= 'a') and (ch <= 'z'):
                self.digit_codes[digit_num] = alpha_codes[ch - 'a']
            elif ch == ' ':
                self.digit_codes[digit_num] = digit_code_map[BLANK_IDX]
            elif ch == '.':
                self.digit_codes[digit_num] = digit_code_map[PERIOD_IDX]
            elif ch == '*':
                self.digit_codes[digit_num] = digit_code_map[ASTERISK_IDX]
            elif ch == '_':
                self.digit_codes[digit_num] = digit_code_map[UNDERSCORE_IDX]
            else:
                # Every unknown character is shown as a dash
                self.digit_codes[digit_num] = digit_code_map[DASH_IDX]

            str_idx += 1
            # Peek at next character. If it's a period, add it to this digit
            if str_value[str_idx] == '.':
                self.digit_codes[digit_num] |= digit_code_map[PERIOD_IDX]
                str_idx += 1
