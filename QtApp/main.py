import sys
import os
from PySide2 import *
from interface_ui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QMainWindow,QMessageBox, QSizeGrip, QSlider, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from PyQt5.QtCore import QRunnable, QThreadPool, QTimer,QTime, Qt
import json
import paho.mqtt.client as mqtt

class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig,self.ax = plt.subplots()
        self.fig.patch.set_facecolor('none')
        super().__init__(self.fig)
        
run =  True
x=[]
y1=[]
y2=[]
x_value = 0
refNhietDo = 0
refDoAm = 0
broker_address = "broker.emqx.io"
broker_port = 1883
username = "emqx"
password = "public"
sub_topic = "sensor_data"
pub_led_topic = "led/data"
pub_fan_topic = "fan_speed"
data_on = "ON"
data_off = "OFF"
######################################################################################################
############################  CLASS MAIN HANDLE ######################################################
######################################################################################################
class mainHandle(Ui_MainWindow):
    def __init__(self):
        self.canv = Canvas()
        self.setupUi(MainWindow)
        self.verticalLayout_5.addWidget(self.canv)
        self.canv.ax2 = self.canv.ax.twinx()
        self.ani = FuncAnimation(self.canv.fig, self.animate, interval=1000)
        self.close_buttom.clicked.connect(self.show_warning_quitbox)
        self.minimum_buttom.clicked.connect(self.minimize_handle)
        self.restore_buttom.clicked.connect(self.restore_or_max_window)
        QSizeGrip(self.size_grip)
        self.homepage_buttom.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.Home_page))
        self.members_buttom.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.Members_page))
        self.setting_buttom.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.Settings_pages))
        self.LedON.clicked.connect(self.led_on)
        self.LedOFF.clicked.connect(self.led_off)
        self.LedON_2.clicked.connect(self.fan_on)
        self.LedOFF_2.clicked.connect(self.fan_off)
    ######################################################################################################
    ############################  HAM XU LY THU PHONG INTERFACE  ########################################
    ######################################################################################################
    def restore_or_max_window(self):
        if MainWindow.isMaximized():
            MainWindow.showNormal()
        else:
            MainWindow.showMaximized()

    ######################################################################################################
    ############################  HAM XU LY THU NHO INTERFACE  ##########################################
    ######################################################################################################
    def minimize_handle(self):
        MainWindow.showMinimized()
    ######################################################################################################
    ############################  HAM HIEN THI WARNING KHI THOAT  ########################################
    ######################################################################################################
    def show_warning_quitbox(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setText("Do you want to quit?")
        self.msg.setWindowTitle("Quit now?")
        self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        retval = self.msg.exec_()
        if retval == QMessageBox.Yes:
            global  run
            run = False
            MainWindow.close()

    ######################################################################################################
    ############################  HAM XU LY DO THI #######################################################
    ######################################################################################################
    def animate(self,i):
            global refNhietDo
            global refDoAm
            global data
            global x
            global y1
            global y2
            x.append(QTime.currentTime().toString('hh:mm:ss'))
            refNhietDo = float(refNhietDo)
            refDoAm = float(refDoAm) 
            y1.append(refNhietDo)
            y2.append(refDoAm)
            if len(x) >= 10:
                x.pop(0)
                y1.pop(0)
                y2.pop(0)
                    
            self.canv.ax.cla()
            self.canv.ax2.cla()
            self.canv.ax.set_ylim([refNhietDo - 10, refNhietDo + 40])
            self.canv.ax2.set_ylim([refDoAm - 10, refDoAm + 10])
            #####################################
            ymax1 = max(y1)
            xpos1 = y1.index(ymax1)
            xmax1 = x[xpos1]
            self.canv.ax.annotate('', xy=(xmax1, ymax1), xytext=(xmax1, ymax1+3),
            arrowprops=dict(facecolor='red', shrink=0.1),
            )
            ####################################
            ymax2 = max(y2)
            xpos2 = y2.index(ymax2)
            xmax2 = x[xpos2]
            self.canv.ax2.annotate('', xy=(xmax2, ymax2), xytext=(xmax2, ymax2+1),
            arrowprops=dict(facecolor='blue', shrink=0.01),
            )
            ####################################
            self.canv.ax.tick_params(axis='x',rotation = 30)
            # self.canv.ax.margins(10)
            self.canv.ax.plot(x, y1, color='red',marker='o',label='Temperature',linewidth=2)
            self.canv.ax.tick_params(axis='y', labelcolor='red')
            self.canv.ax.set_xlabel(' ',fontweight ="bold",color='black')
            #####################################
            self.canv.ax2.plot(x, y2, color='blue',marker='^',label='Humidity',linewidth=2)
            self.canv.ax2.tick_params(axis='y', labelcolor='blue')
            self.canv.ax.set_ylabel('  ',fontweight ="bold",color='black')
            self.canv.ax2.set_ylabel('  ',fontweight ="bold",color='black')
            self.canv.ax2.legend(loc="upper left", shadow=True, fontsize=15)
            self.canv.ax.legend(loc="upper right", shadow=True, fontsize=15)
            self.canv.ax.grid(color='White', alpha=1, linestyle='-', linewidth=2)
            # self.canv.fig.patch.set_facecolor('none')
            self.canv.ax.set_facecolor('#e9e7e7')
            self.canv.ax.tick_params(axis='x',rotation=20,color='black')

    ######################################################################################################
    ############################  HAM CAP NHAT TINH NANG  ################################################
    ######################################################################################################
    def updateLabel(self):  # this func try to update the status of label if it change
        ''' Ham cap nhat giao dien hien tai'''
        global refDoAm
        global refNhietDo
        self.label_6.setText(str(refNhietDo))
        self.label_7.setText(str(refDoAm)) 
    def led_on(self):
         self.stackedWidget_2.setCurrentWidget(self.page_3)
         self.publish_to_mqtt_broker(data_on, broker_address, broker_port, username, password, pub_led_topic)
    def led_off(self):
         self.stackedWidget_2.setCurrentWidget(self.page_4)
         self.publish_to_mqtt_broker(data_off, broker_address, broker_port, username, password, pub_led_topic)
    def fan_on(self):
         self.stackedWidget_3.setCurrentWidget(self.page_6)
         self.publish_to_mqtt_broker(40, broker_address, broker_port, username, password, pub_fan_topic)
    def fan_off(self):
         self.stackedWidget_3.setCurrentWidget(self.page_5)
         self.publish_to_mqtt_broker(20, broker_address, broker_port, username, password, pub_fan_topic)   
    
    def publish_to_mqtt_broker(self, data, broker_address, broker_port, username, password, topic):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT broker")
            else:
                print("Failed to connect to MQTT broker with result code " + str(rc))

        client = mqtt.Client()
        client.username_pw_set(username, password)  # Set the username and password
        client.on_connect = on_connect
        client.connect(broker_address, broker_port, 60)
        client.loop_start()

        client.publish(topic, data)

        client.loop_stop()
        client.disconnect()                           
    ######################################################################################################
    ############################  CLASS RUN ##############################################################
    ######################################################################################################
class Runnable(QRunnable):
    def __init__(self):
        super().__init__()
    
    def run(self):
        def main_mqtt(self):
            global topic
            # Define the callback function for handling incoming messages
            def on_message(client, userdata, msg):
                global refDoAm
                global refNhietDo
                payload = msg.payload.decode()
                # Split the payload into temperature and humidity values
                sensor_data = json.loads(payload)
                refNhietDo = sensor_data['temp']
                refDoAm = sensor_data['hum']
            # Create an MQTT client and set the callback function
            client = mqtt.Client()
            client.on_message = on_message

            # Set username and password
            client.username_pw_set(username, password)
            # Connect to the broker and subscribe to the topic
            client.connect(broker_address, broker_port)
            client.subscribe(sub_topic)

            # Start the MQTT client loop to handle incoming messages
            client.loop_start()
        while run:
            # time.sleep(1)
            try:
                main_mqtt(self)
            except KeyboardInterrupt:
                print("Interrupted")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
    ######################################################################################################
    #########################################  MAIN ######################################################
    ######################################################################################################
    ######################################################################################################
    ######################################################################################################
if __name__ == "__main__":  
    pool = QThreadPool.globalInstance()
    runnable = Runnable()
    pool.start(runnable)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QMainWindow()
    MainWindow.setWindowFlag(Qt.FramelessWindowHint)
    ui = mainHandle()
    MainWindow.show()
    timer = QTimer()
    timer.timeout.connect(ui.updateLabel)
    timer.start(1)
    sys.exit(app.exec_())
