#include "SevSeg.h"
SevSeg sevseg; //Initiate a seven segment controller object

byte ARDUINO_0 = 0;
byte ARDUINO_1 = 1;
byte ARDUINO_2 = 2;
byte ARDUINO_3 = 3;
byte ARDUINO_4 = 4;
byte ARDUINO_5 = 5;
byte ARDUINO_6 = 6;
byte ARDUINO_7 = 7;
byte ARDUINO_8 = 8;
byte ARDUINO_9 = 9;
byte ARDUINO_10 = 10;
byte ARDUINO_11 = 11;
byte ARDUINO_12 = 12;
byte ARDUINO_13 = 13;

void setup() {
    byte numDigits = 4;

    // digitPins number
    // 0 = left digit
    // 3 = right digit 
    
    byte digitPins[] = {ARDUINO_10, ARDUINO_11, ARDUINO_12, ARDUINO_13};

    // segmentPins number
    //   000
    // 5     1
    //   666
    // 4     2
    //   333    1
    
    byte segmentPins[] = {ARDUINO_2, ARDUINO_3, ARDUINO_4, ARDUINO_5, ARDUINO_6, ARDUINO_7, ARDUINO_8, ARDUINO_9};

    // that resistors are placed on the segment pins.
    bool resistorsOnSegments = true; 

    //sevseg.begin(COMMON_CATHODE, numDigits, digitPins, segmentPins, resistorsOnSegments);
    sevseg.begin(COMMON_ANODE, numDigits, digitPins, segmentPins, resistorsOnSegments);

    sevseg.setBrightness(50);
}

void loop() {
    sevseg.setNumber(3141, 3);
    //sevseg.blank();
    //sevseg.setNumber(8);
    sevseg.refreshDisplay(); // Must run repeatedly
}
