#include <./options.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <cJSON.h>
#include <time.h>
#include "esp_sntp.h"

Adafruit_BME280 bme;
HTTPClient http;
int last = -1;

void setup() {
  Serial.begin(9600);
  bool status = bme.begin(0x76);
  if (!status){
    Serial.println("Couldnt find bme280");
    while (1);
  } 
  WiFi.begin(wifi_ssid, wifi_pass);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("trying to connect...");
    delay(1000);
  }
  configTime(3600, 3600, ntp_server);
  sntp_set_sync_interval(86400000);
}

void loop() {
  struct tm time;
  getLocalTime(&time);
  //Serial.println(&time);
  if (time.tm_min % 15 == 0 && time.tm_min != last) {
    last = time.tm_min;
    Serial.printf("%d:%d \n", time.tm_hour, time.tm_min);
    send_data(bme.readTemperature(), bme.readPressure()/100.0f, bme.readHumidity());
  }
  delay(40000);
  
  //send_data(bme.readTemperature(), bme.readPressure()/100.0f, bme.readHumidity());
  //delay(50000);
}

void send_data(float temperature, float pressure, float humidity) {
  if (http.begin(url)) {
    cJSON *json = cJSON_CreateObject();
    cJSON_AddNumberToObject(json, "temperature", (double)temperature);
    cJSON_AddNumberToObject(json, "pressure", (double)pressure);
    cJSON_AddNumberToObject(json, "humidity", (double)humidity);
    int httpcode = http.POST(cJSON_Print(json));
    http.addHeader("Content-Type", "application/json");
    Serial.println(http.getString());
    http.end();
    cJSON_Delete(json);
  }
  else {
    troubleshoot();
  }
}

void troubleshoot() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(wifi_ssid, wifi_pass);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.println("trying to connect...");
      delay(1000);
    }
  }
}