/*
 * SkyGuard AI - ESP32 Automatic Weather Station gateway
 * Sensor: BME280 (temperature + pressure + relative humidity)
 * Transport: Wi-Fi -> HTTP POST -> SkyGuard FastAPI /api/readings
 *
 * Wiring (I2C):
 *   BME280 VIN -> 3V3
 *   BME280 GND -> GND
 *   BME280 SCL -> GPIO 22
 *   BME280 SDA -> GPIO 21
 *
 * Arduino libraries:
 *   Adafruit BME280 Library
 *   Adafruit Unified Sensor
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <time.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
// Use the LAN IP of the machine running FastAPI when ESP32 and backend share Wi-Fi.
const char* SKYGUARD_URL = "http://192.168.1.100:8000/api/readings";
const char* STATION_ID = "AWS01";
const char* DEVICE_ID = "ESP32-AWS01";
const unsigned long SAMPLE_INTERVAL_MS = 10000;

Adafruit_BME280 bme;
unsigned long lastSample = 0;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

String isoTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 1000)) return "";
  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buf);
}

void sendReading(float temperature, float pressure, float humidity) {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  HTTPClient http;
  http.begin(SKYGUARD_URL);
  http.addHeader("Content-Type", "application/json");

  String ts = isoTimestamp();
  String body = "{\"station_id\":\"" + String(STATION_ID) +
                "\",\"temperature\":" + String(temperature, 2) +
                ",\"pressure\":" + String(pressure, 2) +
                ",\"humidity\":" + String(humidity, 2) +
                ",\"timestamp\":\"" + ts +
                "\",\"source\":\"esp32\",\"device_id\":\"" + String(DEVICE_ID) + "\"}";

  int code = http.POST(body);
  Serial.printf("HTTP %d -> %s\n", code, body.c_str());
  if (code > 0) Serial.println(http.getString());
  http.end();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  if (!bme.begin(0x76) && !bme.begin(0x77)) {
    Serial.println("BME280 not found. Check wiring/address.");
    while (true) delay(1000);
  }
  connectWiFi();
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("SkyGuard ESP32 AWS gateway ready.");
}

void loop() {
  if (millis() - lastSample >= SAMPLE_INTERVAL_MS) {
    lastSample = millis();
    float temperature = bme.readTemperature();
    float pressure = bme.readPressure() / 100.0F; // Pa -> hPa
    float humidity = bme.readHumidity();
    if (isfinite(temperature) && isfinite(pressure) && isfinite(humidity)) {
      sendReading(temperature, pressure, humidity);
    } else {
      Serial.println("Invalid BME280 sample; not transmitted.");
    }
  }
}
