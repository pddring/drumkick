/*
  Piezo

  Reads the value from a piezo transducer connected to A0. 
  
  Flashes the built in LED when the piezo is hit and constantly sends the sensor reading via serial port.
*/
#include <Arduino.h>

int sensorPin = A0;   // select the input pin for the potentiometer
int ledPin = LED_BUILTIN;      // select the pin for the LED
int sensorValue = 0;  // variable to store the value coming from the sensor
const int THRESHOLD = 20;
const int DELAY = 2;
const int NOTE_ON_TIME = 150;
const int STARTUP_FLASH_TIME = 50;
const int STARTUP_FLASH_COUNT = 5;
const int FILTER_SIZE = 5;
const int DELAY_BETWEEN_FILTER = 1;
const int SCALE_DIVIDER = 6;
int filter[FILTER_SIZE];
int i = 0;
int total;


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
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  if(sensorValue > THRESHOLD) {
    filter[i] = sensorValue;
    i++;
  }
  if(i == FILTER_SIZE) {
    for(i; i >0; i--) {
      total += filter[i];
    }
    sensorValue = total / SCALE_DIVIDER;
    total = 0;
    Serial.print("KICK:");
    Serial.println(sensorValue);
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    // stop the program for <sensorValue> milliseconds:
    delay(NOTE_ON_TIME);
    // turn the ledPin off:
    digitalWrite(ledPin, LOW);
  } 
}
