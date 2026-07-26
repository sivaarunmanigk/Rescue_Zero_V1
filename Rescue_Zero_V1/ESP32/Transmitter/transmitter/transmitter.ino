#include <SPI.h>
#include <LoRa.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>


static const int RXPin = 4, TXPin = 3; 
static const uint32_t GPSBaud = 9600;


#define NSS 10
#define RST 9
#define DIO0 2



TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

void setup() {
  Serial.begin(9600);
  ss.begin(GPSBaud);

  Serial.println("SOS Transmitter Starting...");

  LoRa.setPins(NSS, RST, DIO0);
  
  if (!LoRa.begin(433E6)) { // Set frequency to 433 MHz 
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  Serial.println("LoRa Initialized.");
}

void loop() {
  // Read GPS data
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      // If we have a valid location, send SOS packet
      if (gps.location.isValid()) {
        sendSOS();
        delay(2000); 
      }
    }
  }
}

void sendSOS() {
  String lat = String(gps.location.lat(), 6);
  String lon = String(gps.location.lng(), 6);
  
  // Format: SOS,lat,lon
  String packet = "SOS," + lat + "," + lon;
  
  Serial.print("Sending: ");
  Serial.println(packet);

  LoRa.beginPacket();
  LoRa.print(packet);
  LoRa.endPacket();
}


