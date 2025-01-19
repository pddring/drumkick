/*
  Ride

  Reads the value from a three piezo transducers connected to A0, A1 and A2 
  
  Flashes the built in LED when the piezo is hit and constantly sends the sensor reading via serial port.
  Range of values sent will be between 10 and 1023
  Whichever piezo detects the largest signal sends one of the following lines:
    BOW: 1023
    EDGE: 1023
    BELL: 1023

  There should be 2x10K resistors forming a potential divider between GND and 5v to bias it to 2.5v (or 512)
  The piezo should be connected to the middle of the potential divider and pin A0
  There should be a 1M resistor in parallel with the piezos
*/

typedef enum {
  STATE_IDLE, STATE_RISING, STATE_FALLING
} states;

#include <Arduino.h>

const int SENSORS = 3;                        // number of piezo sensors
const char * SENSOR_NAMES[SENSORS] = {"BOW", "BELL", "EDGE"};

int sensorPin[SENSORS] = {A0, A1, A2};        // pin connected to the piezo transducer
int ledPin = LED_BUILTIN;                     // select the pin for the built in LED
int sensorValue[SENSORS] = {0, 0, 0};         // stores the absolute sensor value (will be biased to around 512)

const int STARTUP_FLASH_TIME = 50;            // flash speed on startup
const int STARTUP_FLASH_COUNT = 5;            // number of times the LED flashes on startup

const int THRESHOLD_RISING = 60;              // threshold to cross before moving out of idle into rising
const int THRESHOLD_FALLING = 20;             // threshold ot cross before moving out of falling back into idle

const int SAMPLE_FILTER_SIZE = 50;            // number of samples used to calculate the range
int sampleFilter[SENSORS][SAMPLE_FILTER_SIZE];// used to store the raw sample values (rolling window filter)
int iSample[SENSORS];                         // index of the current sample

int previousRange[SENSORS] = {0, 0, 0};       // used to detect if the amplitude is rising or falling
states state[SENSORS] = {                     // state machine starts falling (initial range will be 512, decreasing to 0)
  STATE_FALLING,
  STATE_FALLING,
  STATE_FALLING
};        

void setup() {
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  
  // set up piezo pins as INPUT
  for(int i = 0; i < SENSORS; i++) {
    pinMode(sensorPin[i], INPUT);
  }

  // flash LED on startup
  for(int i = 0; i < STARTUP_FLASH_COUNT; i++) {
    digitalWrite(ledPin, HIGH);
    delay(STARTUP_FLASH_TIME);
    digitalWrite(ledPin, LOW);
    delay(STARTUP_FLASH_TIME);
  }
  Serial.begin(115200);
}

void loop() {
  for(int iPiezo = 0; iPiezo < SENSORS; iPiezo++) {
    // read the value from the sensor:
    sensorValue[iPiezo] = analogRead(sensorPin[iPiezo]);
    sampleFilter[iPiezo][iSample[iPiezo]] = sensorValue[iPiezo];
    iSample[iPiezo]++;
    if(iSample[iPiezo] == SAMPLE_FILTER_SIZE) {
      iSample[iPiezo] = 0;
    }
    
    // calculate min, max and range of all recorded samples in the window filter
    int min = sampleFilter[iPiezo][0];
    int max = sampleFilter[iPiezo][0];
    for(int i = 1; i < SAMPLE_FILTER_SIZE; i++) {
      if(sampleFilter[iPiezo][i] < min) {
        min = sampleFilter[iPiezo][i];
      }
      if(sampleFilter[iPiezo][i] > max) {
        max = sampleFilter[iPiezo][i];
      }
    }
    int range = max - min;

    /* Debugging info: State, sample, range */
    /*
    Serial.print(state);
    Serial.print(" ");
    Serial.print(sensorValue);
    Serial.print(" ");
    Serial.println(range);
    */

    switch(state[iPiezo]) {
      // ignore low level changes (noise) until a spike is detected
      case STATE_IDLE:
        if(range > THRESHOLD_RISING) {
          state[iPiezo] = STATE_RISING;
          previousRange[iPiezo] = range;
        }
        break;

      // spike detected - need to wait until the peak is reached
      case STATE_RISING:
        if(range < previousRange[iPiezo]) {
          digitalWrite(ledPin, HIGH);
          
          // determine which piezo has the highest value
          int max = 0;
          int iMax = 0;
          for(int i = 0; i < SENSORS; i++) {
            Serial.print(SENSOR_NAMES[i]);
            Serial.print(":");
            Serial.print(previousRange[i]);
            Serial.print(" ");
            if(previousRange[i] > max) {
              max = previousRange[i];
              iMax = i;
            }
            state[i] = STATE_FALLING;            
          }
          Serial.println();
        } 
        break;
      
      // peak detected - need to ignore values until level falls low enough to start looking for new spike
      case STATE_FALLING:
        if(range < THRESHOLD_FALLING) {
          state[iPiezo] = STATE_IDLE;
          digitalWrite(ledPin, LOW);
        }
        break;
    }
    previousRange[iPiezo] = range;
  }
}
