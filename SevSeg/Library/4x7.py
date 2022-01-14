import sevseg as svg

sevseg = svg.SevSeg()  # Initiate a seven segment controller object

ARDUINO_0 = 0
ARDUINO_1 = 1
ARDUINO_2 = 2
ARDUINO_3 = 3
ARDUINO_4 = 4
ARDUINO_5 = 5
ARDUINO_6 = 6
ARDUINO_7 = 7
ARDUINO_8 = 8
ARDUINO_9 = 9
ARDUINO_10 = 10
ARDUINO_11 = 11
ARDUINO_12 = 12
ARDUINO_13 = 13

def setup():
    numDigits = 4

    # digitPins number
    # 0 = left digit
    # 3 = right digit
    
    digitPins = [ARDUINO_10, ARDUINO_11, ARDUINO_12, ARDUINO_13]

    # segmentPins number
    #   000
    # 5     1
    #   666
    # 4     2
    #   333    1
    
    segmentPins = [ARDUINO_2, ARDUINO_3, ARDUINO_4, ARDUINO_5, ARDUINO_6, ARDUINO_7, ARDUINO_8, ARDUINO_9]

    # that resistors are placed on the segment pins.
    resistorsOnSegments = True

    # sevseg.begin(svg.COMMON_CATHODE, numDigits, digitPins, segmentPins, resistorsOnSegments)
    sevseg.begin(svg.COMMON_ANODE, numDigits, digitPins, segmentPins, resistorsOnSegments)

    sevseg.set_brightness(50)

setup()

sevseg.set_number(3141, 3)
# sevseg.blank()
# sevseg.set_number(8)
sevseg.refresh_display()  # Must run repeatedly

