/*
  Piezo

  Reads the value from a piezo transducer connected to A0. 
  
  Flashes the built in LED when the piezo is hit and constantly sends the sensor reading via serial port.
*/
#include <Arduino.h>

// pins
int pinBell = A1;               // Piezo connected to bell of the ride
int pinBow = A0;                // Piezo connected to bow of the ride
int pinEdge = A2;               // Piezo connected to edge of the ride
int ledPin = LED_BUILTIN;       // select the pin for the LED

// values read from each piezo
int valueBell = 0;            
int valueBow = 0;
int valueEdge = 0;

// properties
const int THRESHOLD = 20;
const int DELAY = 2;
const int NOTE_ON_TIME = 150;
const int STARTUP_FLASH_TIME = 50;
const int STARTUP_FLASH_COUNT = 5;
const int FILTER_SIZE = 50;
const int SCALE_DIVIDER = 6;

// rolling filters
int filterBell[FILTER_SIZE];
int filterBow[FILTER_SIZE];
int filterEdge[FILTER_SIZE];

int iBell = 0;
int iBow = 0;
int iEdge = 0;
int totalBell;
int totalBow;
int totalEdge;


void setup() {
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  for(int i = 0; i < STARTUP_FLASH_COUNT; i++) {
    digitalWrite(ledPin, HIGH);
    delay(STARTUP_FLASH_TIME);
    digitalWrite(ledPin, LOW);
    delay(STARTUP_FLASH_TIME);
  }
  Serial.begin(115200);
}

void loop() {
  // read the value from the bow of the ride:
  valueBow = analogRead(pinBow);
  if(valueBow > THRESHOLD) {
    filterBow[iBow] = valueBow;
    iBow++;
  }

  // read the value from the edge of the ride:
  valueEdge = analogRead(pinEdge);
  if(valueEdge > THRESHOLD) {
    filterEdge[iEdge] = valueEdge;
    iEdge++;
  }

  // read the value from the bow of the ride:
  valueBell = analogRead(pinBell);
  if(valueBell > THRESHOLD) {
    filterBell[iBell] = valueBell;
    iBell++;
  }

  if(iBow == FILTER_SIZE || iBell == FILTER_SIZE || iEdge == FILTER_SIZE) {
    for(iBow; iBow > 0; iBow--) {
      totalBow += filterBow[iBow];
    }
    for(iEdge; iEdge > 0; iEdge--) {
      totalEdge += filterEdge[iEdge];
    }
    for(iBell; iBell > 0; iBell--) {
      totalBell += filterBell[iBell];
    }  
    valueBow = totalBow / SCALE_DIVIDER;
    valueEdge = totalEdge / SCALE_DIVIDER;
    valueBell = totalBell / SCALE_DIVIDER;
    
    Serial.print("BOW:");
    Serial.print(totalBow);
    Serial.print(" EDGE:");
    Serial.print(totalEdge);
    Serial.print(" BELL:");
    Serial.println(totalBell);

    totalBow = 0;
    totalEdge = 0;
    totalBell = 0;

    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    // stop the program for <sensorValue> milliseconds:
    delay(NOTE_ON_TIME);
    // turn the ledPin off:
    digitalWrite(ledPin, LOW);
  } 
}


