#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Thông tin mạng WiFi
const char* ssid = "Bamos Coffee";
const char *password = "bamosxinchao";

// Thông tin MQTT broker
const char *mqtt_broker = "broker.emqx.io";
const char *mqtt_username = "emqx";
const char *mqtt_password = "public";
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor_data";
const char* mqtt_value = "fan_speed";
const char* mqtt_led = "led/data";

WiFiClient espClient;
PubSubClient client(espClient);

// Chân cảm biến DHT11
#define DHTPIN 15  
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);


// Cấu hình PWM cho động cơ quạt
const int freq = 30000;
const int pwmChannel = 0;
const int resolution = 8;
float fanSpeedValue = 0.0; 

// Chân kết nối đến động cơ quạt
int dutyCycle;
int motor1Pin1 = 27; 
int motor1Pin2 = 26; 
int enable1Pin = 14;

// Chân kết nối đèn LED
int ledPin = 2;

void connectToWiFi() {
    // Kết nối tới mạng WiFi
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void connectToMQTTBroker() {
   // Kết nối tới MQTT broker
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
   // Xử lý callback khi nhận được tin nhắn từ MQTT
  if (strcmp(topic, mqtt_value) == 0) {
    fanCallback(topic, payload, length);
  } else if (strcmp(topic, mqtt_led) == 0) {
    ledCallback(topic, payload, length);
  }
}
void ledCallback(char* topic, byte* payload, unsigned int length) {
  // Xử lý callback cho điều khiển LED
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
  // Xử lý callback cho điều khiển tốc độ quạt
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // In ra mesage nhận được
  Serial.println(message);
  fanSpeedValue = atof(message.c_str());
  

}

void publishData(float temperature, float humidity) {
   // Gửi dữ liệu nhiệt độ và độ ẩm lên MQTT broker
  char payload[50];
  sprintf(payload, "{\"temp\":%.2f,\"hum\":%.2f}", temperature, humidity);
  client.publish(mqtt_topic, payload);
  Serial.println(payload);
}

void setup() {
   // Thiết lập ban đầu
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
  // Vòng lặp chính
  if (!client.connected()) {
    connectToMQTTBroker();
  }
  // Move DC motor forward

  
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  delay(1000);

  if(fanSpeedValue>30){
     dutyCycle = (fanSpeedValue * 255) / 100+125; // Tính toán giá trị tốc độ động cơ quạt dựa vào dữ liệu nhận được
  }
  else{
     dutyCycle = (fanSpeedValue * 255) / 100+75; // Tính toán giá trị tốc độ động cơ quạt dựa vào dữ liệu nhận được

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


  // Delay trước khi publiing new data
  delay(1000);
}
