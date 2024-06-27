#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is connected to GPIO 2 on NodeMCU
#define ONE_WIRE_BUS D4

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

// Define the pin for the pulse sensor
const int pulsePin = A0;

// Variable to store the pulse sensor value
int pulseValue = 0;

void setup() {
  Serial.begin(9600);
  pinMode(pulsePin, INPUT);
  
  // Start the DS18B20 sensor
  sensors.begin();
}

void loop() {
  // Read the pulse sensor value
  pulseValue = analogRead(pulsePin);
  
  // Print the pulse sensor value
  Serial.print("PulseValue:");
  Serial.print(pulseValue);
  Serial.print(",");
  
  // Call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  sensors.requestTemperatures();

  // Print temperature from DS18B20 sensor
  Serial.print("Temperature:");
  Serial.print(sensors.getTempCByIndex(0)); // Celsius
  Serial.println();

  delay(1000);
}
