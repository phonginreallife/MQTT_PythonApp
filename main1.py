import sys
import os
from PySide2 import *
from interface_ui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QMainWindow,QMessageBox, QSizeGrip, QSlider, QGridLayout, QLineEdit
import firebase_admin
from firebase_admin import  db
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from PyQt5.QtCore import QRunnable, QThreadPool, QTimer,QTime, Qt
import time
import csv
import pandas as pd
import numpy as np
import pika
from ast import literal_eval

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
refNhietDo = '0'
refDoAm = '0'
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
        self.horizontalSlider.valueChanged.connect(self.setSpeed)
        self.LedON.clicked.connect(self.ImageLedON)
        self.LedOFF.clicked.connect(self.ImageLedOFF)
        self.LedON_2.clicked.connect(self.ImageLedON_2)
        self.LedOFF_2.clicked.connect(self.ImageLedOFF_2)
    ######################################################################################################
    ############################  HAM XU LY THU PHONG INTERFACES  ########################################
    ######################################################################################################
    def restore_or_max_window(self):
        if MainWindow.isMaximized():
            MainWindow.showNormal()
        else:
            MainWindow.showMaximized()

    ######################################################################################################
    ############################  HAM XU LY THU NHO INTERFACES  ##########################################
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
    ############################  HAM TAT HE THONG #######################################################
    ######################################################################################################
    def stopSpeed(self):
        self.horizontalSlider.setValue(1)
        self.progressBar.setValue(0)

    ######################################################################################################
    ############################  HAM XU LY DU LIEU CHO TOC DO HE THONG ##################################
    ######################################################################################################
    def setSpeed(self):
        if self.horizontalSlider.value() != 1:
            self.progressBar.setValue((self.horizontalSlider.value()-1) * 25)
            db.reference("/DuLieuGuiXuongBoard/SPEED").set(int((self.horizontalSlider.value() - 1) * 25))
        else:
            self.stopSpeed()
    ######################################################################################################
    ############################  HAM XU LY THANH SLIDE POWER ############################################
    ######################################################################################################
    def valueChange(self):
            global speed_firebase
            self.horizontalSlider.setValue(int((speed_firebase / 25) + 1))
            self.progressBar.setValue((self.horizontalSlider.value()-1)*25)
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
            refNhietDo = int(refNhietDo)
            refDoAm = int(refDoAm) 
            y1.append(refNhietDo)
            y2.append(refDoAm)
            if(len(x)> 10):
                for m in range(10):
                    x.pop(m)
                    y1.pop(m)
                    y2.pop(m)
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
    def ImageLedON(self):
         self.stackedWidget_2.setCurrentWidget(self.page_3)
         self.publicerLed1(1)
    def ImageLedOFF(self):
         self.stackedWidget_2.setCurrentWidget(self.page_4)
         self.publicerLed1(0)        
    def ImageLedON_2(self):
         self.stackedWidget_3.setCurrentWidget(self.page_6)
         self.publicerLed2(1)
    def ImageLedOFF_2(self):
         self.stackedWidget_3.setCurrentWidget(self.page_5)
         self.publicerLed2(0)            
    def publicerLed1(self, check):
                self.check = check
                # If you want to have a more secure SSL authentication, use ExternalCredentials object instead
                credentials = pika.PlainCredentials(username='thebigrabbit', password='MyS3cur3Passwor_d', erase_on_connect=True)
                parameters = pika.ConnectionParameters(host='18.222.254.163', port=5672, virtual_host='cherry_broker', credentials=credentials)
                # We are using BlockingConnection adapter to start a session. It uses a procedural approach to using Pika and has most of the asynchronous expectations removed
                connection = pika.BlockingConnection(parameters)
                # A channel provides a wrapper for interacting with RabbitMQ
                channel = connection.channel()
                if self.check == 1:
                    message = '1'
                else:
                     message = '0'               
                # For the sake of simplicity, we are not declaring an exchange, so the subsequent publish call will be sent to a Default exchange that is predeclared by the broker
                # while True:
                exchange_name = 'led1_data'
                channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
                routing_key = 'my_topic_key'
                channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
                    # Print the message for debugging purposes
                print(f"Published Led 1 Data: {message}")
                    # Wait for some time before publishing the next message
                # time.sleep(1)
                # Safely disconnect from RabbitMQ
                connection.close()
    def publicerLed2(self, check):
                self.check = check
                # If you want to have a more secure SSL authentication, use ExternalCredentials object instead
                credentials = pika.PlainCredentials(username='thebigrabbit', password='MyS3cur3Passwor_d', erase_on_connect=True)
                parameters = pika.ConnectionParameters(host='18.222.254.163', port=5672, virtual_host='cherry_broker', credentials=credentials)

                # We are using BlockingConnection adapter to start a session. It uses a procedural approach to using Pika and has most of the asynchronous expectations removed
                connection = pika.BlockingConnection(parameters)
                # A channel provides a wrapper for interacting with RabbitMQ
                channel = connection.channel()
                if self.check == 1:
                    message = '1'
                else:
                     message = '0'               
                # For the sake of simplicity, we are not declaring an exchange, so the subsequent publish call will be sent to a Default exchange that is predeclared by the broker
                # while True:
                exchange_name = 'led2_data'
                channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
                routing_key = 'my_topic_key'
                channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
                    # Print the message for debugging purposes
                print(f"Published Led 2 Data: {message}")

                    # Wait for some time before publishing the next message
                # time.sleep(1)
                # Safely disconnect from RabbitMQ
                connection.close()              
    ######################################################################################################
    ############################  CLASS RUN ##############################################################
    ######################################################################################################
class Runnable(QRunnable):
    def __init__(self):
        super().__init__()
    
    def run(self):
        def main_mqtt(self):
            credentials = pika.PlainCredentials('thebigrabbit', 'MyS3cur3Passwor_d')
            parameters = pika.ConnectionParameters(host='18.222.254.163', port=5672, virtual_host='cherry_broker', credentials=credentials)    
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            exchange_name = 'topic_logs' 
            channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
            routing_key = 'my.topic.key'
            queue_name = 'topic_logs'
            channel.queue_declare(queue_name)
            channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
            # Since RabbitMQ works asynchronously, every time you receive a message, a callback function is called.
            def callback(ch, method, properties, body):
                #print("Received message: %s" % body)
                body = literal_eval(body.decode('utf-8'))
                global refNhietDo
                global refDoAm
                refNhietDo = body['temp']
                refDoAm = body['hum']
            # Consume a message from a queue. 
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(' [*] Waiting for messages. To exit press CTRL+C')          
            # Start listening for messages to consume
            channel.start_consuming()
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
