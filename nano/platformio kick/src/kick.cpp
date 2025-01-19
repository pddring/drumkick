/*
  Piezo

  Reads the value from a piezo transducer connected to A0. 
  
  Flashes the built in LED when the piezo is hit and constantly sends the sensor reading via serial port.
  Range of values sent will be between 10 and 1023
  Values sent in the form:
    KICK: 1023

  There should be 2x10K resistors forming a potential divider between GND and 5v to bias it to 2.5v (or 512)
  The piezo should be connected to the middle of the potential divider and pin A0
  There should be a 1M resistor in parallel with the piezo
*/

typedef enum {
  STATE_IDLE, STATE_RISING, STATE_FALLING
} states;

#include <Arduino.h>

int sensorPin = A0;                           // pin connected to the piezo transducer
int ledPin = LED_BUILTIN;                     // select the pin for the built in LED
int sensorValue = 0;                          // stores the absolute sensor value (will be biased to around 512)

const int STARTUP_FLASH_TIME = 50;            // flash speed on startup
const int STARTUP_FLASH_COUNT = 5;            // number of times the LED flashes on startup

const int THRESHOLD_RISING = 20;              // threshold to cross before moving out of idle into rising
const int THRESHOLD_FALLING = 10;             // threshold ot cross before moving out of falling back into idle

const int SAMPLE_FILTER_SIZE = 50;            // number of samples used to calculate the range
int sampleFilter[SAMPLE_FILTER_SIZE];         // used to store the raw sample values (rolling window filter)
int iSample = 0;                              // index of the current sample

int previousRange = 0;                        // used to detect if the amplitude is rising or falling
states state = STATE_FALLING;                 // state machine starts falling (initial range will be 512, decreasing to 0)

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
  sampleFilter[iSample] = sensorValue;
  iSample++;
  if(iSample == SAMPLE_FILTER_SIZE) {
    iSample = 0;
  }
  
  // calculate min, max and range of all recorded samples in the window filter
  int min = sampleFilter[0];
  int max = sampleFilter[0];
  for(int i = 1; i < SAMPLE_FILTER_SIZE; i++) {
    if(sampleFilter[i] < min) {
      min = sampleFilter[i];
    }
    if(sampleFilter[i] > max) {
      max = sampleFilter[i];
    }
  }
  int range = max - min;

  /* Debugging info: State, sample, range
  Serial.print(state);
  Serial.print(" ");
  Serial.print(sensorValue);
  Serial.print(" ");
  Serial.println(range);
  */

  switch(state) {
    // ignore low level changes (noise) until a spike is detected
    case STATE_IDLE:
      if(range > THRESHOLD_RISING) {
        state = STATE_RISING;
        previousRange = range;
      }
      break;

    // spike detected - need to wait until the peak is reached
    case STATE_RISING:
      if(range < previousRange) {
        state = STATE_FALLING;
        digitalWrite(ledPin, HIGH);
        Serial.print("KICK:");
        Serial.println(previousRange);
      } else {
        previousRange = range;
      }
      break;
    
    // peak detected - need to ignore values until level falls low enough to start looking for new spike
    case STATE_FALLING:
      if(range < THRESHOLD_FALLING) {
        state = STATE_IDLE;
        digitalWrite(ledPin, LOW);
      }
      break;
  }
}
