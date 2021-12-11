
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>

Adafruit_MPU6050 mpu;

const char name = 'l'; // l or r

// WiFi network name and password:
//const char * networkName = "Mi Phone"; // specify SSID here
//const char * networkPswd = "forlab18only"; // specify password here
const char * networkName = "MGTS_GPON_8D20"; // specify SSID here
const char * networkPswd = "mQU3kaXP"; // specify password here

//IP address to send UDP data to:
// either use the ip address of the server or 
// a network broadcast address
const char * udpAddress = "192.168.1.5"; // specify server IP here
const int udpPort = 60001; // specify server port here

//Are we currently connected?
boolean connected = false;

//The udp library class
WiFiUDP udp;

void setup(){
  // Initilize hardware serial:
  Serial.begin(115200);
  
  //Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);

  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens
  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
     Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);

  mpu.setGyroRange(MPU6050_RANGE_250_DEG);

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  delay(100);
  Serial.println("");
  delay(100);
}

void loop(){
  //only send data when connected
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  if(connected){
    //Send a packet
    udp.beginPacket(udpAddress,udpPort);
    udp.printf("%c, %lf, %lf, %lf, %lf, %lf, %lf\n", name,
                              a.acceleration.x, a.acceleration.y, a.acceleration.z,
                              g.gyro.x, g.gyro.y, g.gyro.z);

    udp.endPacket();
  }
  Serial.printf("name: %c; connected: %d; data: %lf, %lf, %lf, %lf, %lf, %lf\n",  name, connected,
                              a.acceleration.x, a.acceleration.y, a.acceleration.z,
                              g.gyro.x, g.gyro.y, g.gyro.z);
  delayMicroseconds(27778);
}

void connectToWiFi(const char * ssid, const char * pwd){
  Serial.println("Connecting to WiFi network: " + String(ssid));

  // delete old config
  WiFi.disconnect(true);
  //register event handler
  WiFi.onEvent(WiFiEvent);
  
  //Initiate connection
  WiFi.begin(ssid, pwd);

  Serial.println("Waiting for WIFI connection...");
}
//wifi event handler
void WiFiEvent(WiFiEvent_t event){
    switch(event) {
      case ARDUINO_EVENT_WIFI_STA_GOT_IP:
          //When connected set 
          Serial.print("WiFi connected! IP address: ");
          Serial.println(WiFi.localIP());  
          //initializes the UDP state
          //This initializes the transfer buffer
          udp.begin(WiFi.localIP(),udpPort);
          connected = true;
          break;
      case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
          Serial.println("WiFi lost connection");
          connected = false;
          break;
      default: break;
    }
}
