MQTT_PythonApp 
This app uses Pyside2, Qt Designer designing a interface to control temperature, humidity, led and fan engine parallelly. The App communicate with ESP32 through MQTT protocols. 
ESP32 connects DHT11 as well as Fan engine to send temp, hum and receive fan speed data through MQTT broker. 

Prerequisites:

•	python 3.10.x 
•	Adruino IDE 

Requirements:

•	pip install PySide2 

•	pip install Paho 

•	pip install matplotlib

•	pip install PyQt5

 Guiding: 
 
•	Step 1: Open CMD in your computer, you’d better create a new folder and store inside it, this will prevent any future confusion. git clone https://github.com/phonginreallife/MQTT_PythonApp.git 

•	Step 2: Open the repository and run main file: python main.py


•	Step 3: Connect your devices and sensors with ESP32 and then connect with your Computer: 

Pushing .ion code to ESP32, when you saw the sending message (include sent temperature, huminity as well as recieved fan speed),mean you have successfully setup it. 

Important Note: Changing wifi SSID and password in ESP32 code.
