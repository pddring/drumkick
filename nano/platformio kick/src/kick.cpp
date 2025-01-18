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
const int NOTE_ON_TIME = 40;
const int STARTUP_FLASH_TIME = 50;
const int STARTUP_FLASH_COUNT = 5;
const int FILTER_SIZE = 50;
const int SCALE_DIVIDER = 128;
const int IDLE_THRESHOLD = 50;
int filter[FILTER_SIZE];
unsigned int idle = 0;
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
  if(idle > IDLE_THRESHOLD) {
    i = 0;
  }
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  if(sensorValue > THRESHOLD) {
    filter[i] = sensorValue;
    i++;
    idle = 0;
  } else {
    idle++;
  }
  if(i == FILTER_SIZE) {
    digitalWrite(ledPin, HIGH);
    for(i; i > 0; i--) {
      total += filter[i];
    }
    sensorValue = total / SCALE_DIVIDER;
    total = 0;
    Serial.print("KICK:");
    Serial.println(sensorValue);
    
    // prevent machine gunning
    delay(NOTE_ON_TIME);
    digitalWrite(ledPin, LOW);
  } 
}
