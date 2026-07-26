#include <SPI.h>
#include <LoRa.h>


#define NSS 10
#define RST 9
#define DIO0 2



void setup() {
  Serial.begin(9600); 
  while (!Serial);

  Serial.println("SOS Receiver Starting...");

  LoRa.setPins(NSS, RST, DIO0);
  
  if (!LoRa.begin(433E6)) { 
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Received a packet
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    
    // Forward to Serial for Python backend
    Serial.println(incoming);
  }
}
