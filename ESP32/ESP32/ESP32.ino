#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>


const char* ssid = "Bamos Coffee";
const char *password = "bamosxinchao";
const char *mqtt_broker = "broker.emqx.io";
const char *mqtt_username = "emqx";
const char *mqtt_password = "public";
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor_data";
const char* mqtt_value = "fan_speed";
const char* mqtt_led = "led/data";

WiFiClient espClient;
PubSubClient client(espClient);

// Replace with your DHT11 sensor pin
#define DHTPIN 15  
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int freq = 30000;
const int pwmChannel = 0;
const int resolution = 8;
float fanSpeedValue = 0.0; 
int dutyCycle;
int motor1Pin1 = 27; 
int motor1Pin2 = 26; 
int enable1Pin = 14;
int ledPin = 2;

void connectToWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void connectToMQTTBroker() {
    Serial.print("Connecting to MQTT broker...");
    if (client.connect("ESP32")) {
      Serial.println("\nConnected to MQTT broker");
      client.subscribe(mqtt_value);
      client.subscribe(mqtt_led);
    } else {
      Serial.print("\nFailed with state ");
      Serial.print(client.state());
      delay(1000);
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, mqtt_value) == 0) {
    fanCallback(topic, payload, length);
  } else if (strcmp(topic, mqtt_led) == 0) {
    ledCallback(topic, payload, length);
  }
}
void ledCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("LED control message received on topic: ");
  Serial.println(topic);
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Received message: ");
  Serial.println(message);
  
  // Control LED based on message
  if (message == "ON") {
    digitalWrite(ledPin, HIGH);
    Serial.println("LED turned ON");
  } else if (message == "OFF") {
    digitalWrite(ledPin, LOW);
    Serial.println("LED turned OFF");
  }
}
void fanCallback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // Print the received message
  Serial.println(message);
  fanSpeedValue = atof(message.c_str());
  

}

void publishData(float temperature, float humidity) {
  char payload[50];
  sprintf(payload, "{\"temp\":%.2f,\"hum\":%.2f}", temperature, humidity);
  client.publish(mqtt_topic, payload);
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(enable1Pin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  ledcSetup(pwmChannel, freq, resolution);
  ledcAttachPin(enable1Pin, pwmChannel);
  ledcWrite(pwmChannel, dutyCycle);
  
  connectToWiFi();
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  // Initialize DHT11 sensor
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    connectToMQTTBroker();
  }
  // Move DC motor forward

  
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  delay(1000);

  if(fanSpeedValue>30){
     dutyCycle = (fanSpeedValue * 255) / 100+125; // calculate duty cycle based on fan speed percentage
  }
  else{
     dutyCycle = (fanSpeedValue * 255) / 100+75; // calculate duty cycle based on fan speed percentage

 }
   ledcWrite(pwmChannel, dutyCycle);
   client.loop(); // Process incoming MQTT messages

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read data from DHT11 sensor");
    return;
  }

  // Publish the data to the MQTT broker
  publishData(temperature, humidity);


  // Delay before publishing the next set of data
  delay(1000);
}
