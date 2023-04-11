import sys
import os
from PySide2 import *
from interface_ui import *
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



class Canvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig,self.ax = plt.subplots()
        self.fig.patch.set_facecolor('none')
        super().__init__(self.fig)
        

cred_obj = firebase_admin.credentials.Certificate(".\iotwatering-3893b-firebase-adminsdk-54pek-4524dc9c11.json")
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://iotwatering-3893b-default-rtdb.asia-southeast1.firebasedatabase.app'
})

x=[]
y1=[]
y2=[]
x_value = 0
refNhietDo = 0
refDoAm = 0
run = True
refStatesuccess = 0
datetime = db.reference("/DuLieuBoard/ThoiGian").get()
temp_value_mode = db.reference("/DuLieuGuiXuongBoard/MODE").get()
temp_value_type = db.reference("/ThongSoBoard/TYPE").get()
float_fire_base = db.reference("/DuLieuBoard/FLOAT").get()
speed_fire_base= db.reference("/DuLieuGuiXuongBoard/SPEED").get()
mode_firebase = temp_value_mode
type_firebase = temp_value_type
speed_firebase = speed_fire_base
state_current = db.reference("/DuLieuBoard/State").get()
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
        self.horizontalSlider.setValue(int(db.reference("/DuLieuGuiXuongBoard/SPEED").get()/25)+1)
        self.progressBar.setValue(int(db.reference("/DuLieuGuiXuongBoard/SPEED").get()))
        self.horizontalSlider.valueChanged.connect(self.setSpeed)
        self.Type_configure.hide()
        self.show_page_configure.hide()
        self.label_16.hide()
        self.upDatesFirebase()
        self.Mode_configure.currentTextChanged.connect(self.modeConfigureFix)


    ######################################################################################################
    ############################  HAM XU LY TAB SETTINGS  ################################################
    ######################################################################################################
    def modeConfigureFix(self):
      if self.Mode_configure.currentText() == "Automation":
               self.label_16.show()
               self.Type_configure.show()
               self.show_page_configure.show()
               self.Type_configure.currentTextChanged.connect(self.pageConfigure)
               db.reference("/DuLieuGuiXuongBoard/MODE").set(0)
               global type_firebase
               if (type_firebase == 1):
                   self.Type_configure.setCurrentText("Time")
                   self.pageConfigure()
               else:
                   self.Type_configure.setCurrentText("Temperature")
                   self.pageConfigure()
      else:
          self.label_16.hide()
          self.Type_configure.hide()
          self.show_page_configure.hide()
          db.reference("/DuLieuGuiXuongBoard/MODE").set(1)
    ######################################################################################################
    ############################  HAM HIEN THI INTERFACES THEO LUA CHON ##################################
    ######################################################################################################
    def pageConfigure(self):
        if self.Type_configure.currentText() == "Time":
            self.show_page_configure.setCurrentWidget(self.page_2)
            self.confirm_time.clicked.connect(self.firebase_time_set)
        if self.Type_configure.currentText() == "Temperature":
            self.show_page_configure.setCurrentWidget(self.page)
            self.confirm_temp.clicked.connect(self.firebase_temp_set)
    ######################################################################################################
    ############################  HAM XU LY DU LIEU CAP NHAT THEO NHIET DO ###############################
    ######################################################################################################
    def firebase_temp_set(self):
        if self.temp_min.displayText() < self.temp_max.displayText():
            db.reference("/ThongSoBoard/NhietDoMax").set(int(self.temp_max.displayText()))
            db.reference("/ThongSoBoard/NhietDoMin").set(int(self.temp_min.displayText()))
            db.reference("/DuLieuGuiXuongBoard/StateDown").set(1)
            for i in range(10):
                global refStatesuccess
                time.sleep(1)
                if refStatesuccess == 1:
                    self.text_complete.setText("<font color='green'>updated successfully!</font>")
                    db.reference("/DuLieuGuiXuongBoard/StateDown").set(0)
                    break
                else:
                    self.text_complete.setText("<font color='red'>error! can't detect your divice</font>")
            db.reference("/ThongSoBoard/TYPE").set(0)
        else:
            self.show_warning()

    ######################################################################################################
    ############################  HAM XU LY DU LIEU CAP NHAT THEO THOI GIAN ##############################
    ######################################################################################################
    def firebase_time_set(self):
        x = int(self.hh_delivery.currentText())*3600 + int(self.mm_delivery.currentText())*60 + int(self.ss_delivery.currentText())
        y = int(self.hh_receive.currentText())*3600 + int(self.mm_receive.currentText())*60 + int(self.ss_receive.currentText())
        if y > x:
            self.time_start = str(self.hh_delivery.currentText()) + ":" + str(
                self.mm_delivery.currentText())+ ":" + str(self.ss_delivery.currentText())
            self.time_end = str(self.hh_receive.currentText())+":" + str(self.mm_receive.currentText())+ ":" + str(self.ss_receive.currentText())
            db.reference("/ThongSoBoard/TimeStart").set(self.time_start)
            db.reference("/ThongSoBoard/TimeStop").set(self.time_end)
            db.reference("/DuLieuGuiXuongBoard/StateDown").set(1)
            for i in range(10):
                global refStatesuccess
                time.sleep(1)
                if refStatesuccess == 1:
                    self.text_complete_2.setText("<font color='green'>updated successfully!</font>")
                    db.reference("/DuLieuGuiXuongBoard/StateDown").set(0)
                    break
                else:
                    self.text_complete_2.setText("<font color='red'>Error! Can't detect your divice</font>")
            db.reference("/ThongSoBoard/TYPE").set(1)
        else:
            self.show_warning()

    ######################################################################################################
    ############################  HAM HIEN THI WARNING KHI NHAP SAI  #####################################
    ######################################################################################################
    def show_warning(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setText("Please enter values correctly!")
        self.msg.setWindowTitle("Error")
        self.msg.setStandardButtons(QMessageBox.Yes| QMessageBox.Cancel)
        retval = self.msg.exec_()
        if retval == QMessageBox.Yes or QMessageBox.Cancel:
            pass
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
            refNhietDo = db.reference("/DuLieuBoard/NhietDo").get()
            refDoAm = db.reference("/DuLieuBoard/DoAm").get()
            global data
            global x
            global y1
            global y2
            x.append(QTime.currentTime().toString('hh:mm:ss'))
            y1.append(refNhietDo)
            y2.append(refDoAm)

            if(len(x)> 4):
                for m in range(len(x)-4):
                    x.pop(m)
                    y1.pop(m)
                    y2.pop(m)
            self.canv.ax.cla()
            self.canv.ax2.cla()
            self.canv.ax.set_ylim([refNhietDo - 5, refNhietDo + 20])
            self.canv.ax2.set_ylim([refDoAm - 5, refDoAm + 5])
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
            self.canv.ax.set_ylabel(' Temperature ',fontweight ="bold",color='black')
            self.canv.ax2.set_ylabel(' Humidity ',fontweight ="bold",color='black')
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
        currentTime = QTime.currentTime()
        displayTxt = currentTime.toString('hh:mm:ss')
        self.time_on_sys.setText(displayTxt)
        global datetime
        x = datetime.split()
        self.time_on_board.setText(x[0])
        self.day_on_board.setText(x[1])
        self.day_on_sys.setText(x[1])
        global speed_firebase
        global speed_fire_base
        speed_fire_base = db.reference("/DuLieuGuiXuongBoard/SPEED").get()
        if speed_firebase != speed_fire_base:
            speed_firebase = speed_fire_base
            self.valueChange()
        float_fire_base = db.reference("/DuLieuBoard/FLOAT").get()
        if float_fire_base == 1:
            self.stackedWidget_2.setCurrentWidget(self.page_full)
            self.valueChange()
        if float_fire_base == 0:
            self.stackedWidget_2.setCurrentWidget(self.page_low)
            self.stopSpeed()
    ######################################################################################################
    ############################  HAM CAP NHAT DU LIEU MUC NUOC TREN FIREBASE  ###########################
    ######################################################################################################
    def checkWaterLevel(self):
        '''Ham cap nhat du lieu muc nuoc tren firebase'''
        global speed_firebase
        if float_fire_base == 1:
            self.stackedWidget.setCurrentWidget(self.page_full)
            self.horizontalSlider.setValue(int(speed_firebase / 25) + 1)
        else:
            self.stackedWidget.setCurrentWidget(self.page_low)
            self.horizontalSlider.setValue(1)

    ######################################################################################################
    ############################  HAM CAP NHAT DU LIEU FIREBASE  #########################################
    ######################################################################################################
    def upDatesFirebase(self):
        '''Ham cap nhat du lieu firebase'''
        global mode_firebase
        global type_firebase
        global float_fire_base
        if (mode_firebase == 0):
            self.Mode_configure.setCurrentText("Automation")
            self.modeConfigureFix()
        else:
            self.Mode_configure.setCurrentText("Manual")
            self.modeConfigureFix()
        self.checkWaterLevel()
    ######################################################################################################
    ############################  CLASS RUN ##############################################################
    ######################################################################################################
class Runnable(QRunnable):
    def __init__(self):
        super().__init__()
        self.fieldnames = ["x_value","NhietDo","DoAm"]
        with open('data.csv','w') as csv_file:
            self.csv_writer = csv.DictWriter(csv_file,fieldnames=self.fieldnames)
            self.csv_writer.writeheader()
    def run(self):
        while run:
            time.sleep(1)
            global refStatesuccess
            global datetime
            global mode_firebase
            global type_firebase
            global temp_value_type
            global temp_value_mode
            global float_fire_base
            datetime = db.reference("/DuLieuBoard/ThoiGian").get()
            refStatesuccess = db.reference("/DuLieuBoard/Statesuccess").get()
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