/*
  Piezo

  Reads the value from a piezo transducer connected to A0. 
  
  Flashes the built in LED when the piezo is hit and constantly sends the sensor reading via serial port.
*/

int sensorPin = A0;   // select the input pin for the potentiometer
int ledPin = LED_BUILTIN;      // select the pin for the LED
int sensorValue = 0;  // variable to store the value coming from the sensor
const int THRESHOLD = 2;
const int DELAY = 2;
const int NOTE_ON_TIME = 50;
void setup() {
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  Serial.begin(19200);
}

void loop() {
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  if(sensorValue > THRESHOLD) {
    Serial.println(sensorValue);
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    // stop the program for <sensorValue> milliseconds:
    delay(NOTE_ON_TIME);
    // turn the ledPin off:
    digitalWrite(ledPin, LOW);
  }
  // stop the program for <sensorValue> milliseconds:
  delay(DELAY);
}
