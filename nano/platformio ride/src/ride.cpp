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
const int THRESHOLD = 10;
const int DELAY = 2;
const int NOTE_ON_TIME = 40;
const int STARTUP_FLASH_TIME = 50;
const int STARTUP_FLASH_COUNT = 5;
const int FILTER_SIZE = 50;
const int PRE_SCALE_DIVIDER = 4;
const int POST_SCALE_DIVIDER_BELL = 32;
const int POST_SCALE_DIVIDER_BOW = 24;
const int POST_SCALE_DIVIDER_EDGE = 32;
const unsigned int IDLE_THRESHOLD = 15;

// rolling filters
int filterBell[FILTER_SIZE];
int filterBow[FILTER_SIZE];
int filterEdge[FILTER_SIZE];

int iBell = 0;
int iBow = 0;
int iEdge = 0;
long totalBell;
long totalBow;
long totalEdge;

unsigned int idleBell = 0;
unsigned int idleBow = 0;
unsigned int idleEdge = 0;
unsigned int totalIdle = 0;


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
  if(iBow == FILTER_SIZE || iBell == FILTER_SIZE || iEdge == FILTER_SIZE) {
    for(iBow; iBow > 0; iBow--) {
      totalBow += filterBow[iBow] / PRE_SCALE_DIVIDER;
    }
    totalBow /= POST_SCALE_DIVIDER_BOW;
    
    for(iEdge; iEdge > 0; iEdge--) {
      totalEdge += filterEdge[iEdge] / PRE_SCALE_DIVIDER;
    }
    totalEdge /= POST_SCALE_DIVIDER_EDGE;

    for(iBell; iBell > 0; iBell--) {
      totalBell += filterBell[iBell] / PRE_SCALE_DIVIDER;
    }  
    totalBell /= POST_SCALE_DIVIDER_BELL;
    
    if(totalEdge > totalBow && totalEdge > totalBell) {
      totalIdle = idleBow + idleBell;
      if(totalIdle > IDLE_THRESHOLD) {
        // Serial.println("Ignore Edge");
      } else {
        Serial.print("EDGE:");
        Serial.println(totalEdge);
      }
    }
    if(totalBow >= totalEdge && totalBow >= totalBell) {
      totalIdle = idleEdge + idleBell;
      if(totalIdle > IDLE_THRESHOLD) {
        // Serial.println("Ignore Bow");
      } else {
        Serial.print("BOW:");
        Serial.println(totalBow);
      }
    }
    if(totalBell > totalBow && totalBell > totalEdge) {
      totalIdle = idleEdge + idleBow;
      if(totalIdle > IDLE_THRESHOLD) {
        // Serial.println("Ignore Bell");
      } else {
        Serial.print("BELL:");
        Serial.println(totalBell);
      }
    }
  
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

  // read the value from the bow of the ride:
  valueBow = analogRead(pinBow);
  filterBow[iBow] = valueBow;
  iBow++;
  if(valueBow > THRESHOLD) {
    idleBow = 0;
  } else {
    idleBow++;
  }

  // read the value from the edge of the ride:
  valueEdge = analogRead(pinEdge);
  filterEdge[iEdge] = valueEdge;
  iEdge++;
  if(valueEdge > THRESHOLD) {  
    idleEdge = 0;
  } else {
    idleEdge++;
  }

  // read the value from the bow of the ride:
  valueBell = analogRead(pinBell);
  filterBell[iBell] = valueBell;
  iBell++;
  if(valueBell > THRESHOLD) {
    idleBell = 0;
  } else {
    idleBell++;
  }

   
}


