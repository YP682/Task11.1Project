#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>

// WiFi credentials
const char* ssid = "***";
const char* password = "***";

// MQTT broker details
const char* broker = "broker.emqx.io";
const int port = 1883;
const char* temperatureTopic = "home/temperature";
const char* humidityTopic = "home/humidity";
const char* lightTopic = "home/light";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

#define DHTPIN 2     // Pin connected to the DHT sensor
#define DHTTYPE DHT11   // DHT 11
DHT dht(DHTPIN, DHTTYPE);

BH1750 lightMeter;

void setup() {
  Serial.begin(9600);
  dht.begin();
  Wire.begin();
  
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println(F("Could not find a valid BH1750 sensor, check wiring!"));
    while (1);
  }

  connectWiFi();
  client.setServer(broker, port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read humidity and temperature from DHT11
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float lux = lightMeter.readLightLevel();

  if (!isnan(h) && !isnan(t)) {
    String temperatureStr = String(t);
    String humidityStr = String(h);
    client.publish(temperatureTopic, temperatureStr.c_str());
    client.publish(humidityTopic, humidityStr.c_str());
  } else {
    Serial.println("Failed to read from DHT sensor!");
  }

  if (lux != -1) {
    String lightStr = String(lux);
    client.publish(lightTopic, lightStr.c_str());
  } else {
    Serial.println("Failed to read from BH1750 sensor!");
  }

  delay(2000);
}

void connectWiFi() {
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker...");
    if (client.connect("arduinoClient")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
