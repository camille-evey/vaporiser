# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 13:42:47 2025

@author: cgennet
"""
import serial, sys
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QDoubleSpinBox, QPushButton
from collections import defaultdict

    
class Fenetre(QMainWindow):
    def __init__(self, port = ['/dev/tty.usbmodem*', '/dev/ttyACM0', 'COM11'], timeout = 0.1):
        QMainWindow.__init__(self)
        self.setWindowTitle("Programme Vapo")
        self.setMinimumSize(700, 400) 
        self.resize(1080,720)
        
        #open qss file pour la stylesheet
        File = open("VapoStyle.qss",'r')
        with File:
                 qss = File.read()
                 self.setStyleSheet(qss)
                 
        self.centralwidget = QWidget()
        self.centralwidget.setObjectName("leWidgetCentral")
        self.setCentralWidget(self.centralwidget)
        
        #Initialisation de la température 
        self.T1 = 0
        self.T2 = 0
        
        #Initialisation du disctionnaire pour les datas 
        self.state = defaultdict(lambda: 0.)
            			 
        #Gestion du timer pour la maj de la température
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        
        #On ouvre le port pour communiquer avec la carte 
        self.board = serial.Serial('COM14', timeout = timeout)      
        self.rbuf = b'' #ca c'est le buffer de lecture, pour l'instant vide
        self.instructions = [] #ca c'est pour découper le buffer en différentes instructions
        self.board.write(b'\r') #et ca envoie "entrée" à la carte, sans doute pour faire coucou
      
        # on crée un objet icon pour gérer les vannes
        iconPump = QIcon()
        iconPump.addPixmap(QPixmap('pump_red.png'), QIcon.Normal, QIcon.Off)
        iconPump.addPixmap(QPixmap('pump_lightblue.png'), QIcon.Normal, QIcon.On)

       #Define widgets
        self.label = QLabel("Temp 1",parent=self.centralwidget)
        self.label.resize(80,30)
        self.TempRead1 = QDoubleSpinBox(parent=self.centralwidget)
        self.TempRead1.resize(76, 25)
        self.TempRead1.setReadOnly(True)
        self.label1 = QLabel("Temp 2",parent=self.centralwidget)
        self.label1.resize(80,30)
        self.TempRead2 = QDoubleSpinBox(parent=self.centralwidget)
        self.TempRead2.resize(76, 25)
        self.TempRead2.setReadOnly(True)
        self.label0 = QLabel("Contrôle température",parent=self.centralwidget)
        self.label0.resize(125,30)
        self.TempSend = QDoubleSpinBox(parent=self.centralwidget)
        self.TempSend.resize(76, 25)
        self.TempSend.valueChanged.connect(self.setTemperature)
        
        self.Pumps = []
        self.Labels = []
        for i, [name, label] in enumerate(zip(['V1','V2','V3','V4'],
                               ['Vanne Entrée', 'Vanne Sortie', 'Vanne mid', 'Vanne Bypass'])):
            self.Pumps.append(QPushButton(icon=iconPump, 
                                     parent=self.centralwidget))
            self.Pumps[i].setIconSize(QtCore.QSize(100,100))
            self.Pumps[i].setCheckable(True)
            self.Pumps[i].setObjectName(name)
            self.Pumps[i].clicked.connect(self.onBtnClicked)
            self.Labels.append(QLabel(label, parent=self.centralwidget))
            self.Labels[i].resize(80,30)
        
        # Re-scaling the interface
        self.resizeUi(self.width(), self.height())

    @QtCore.pyqtSlot("QResizeEvent")
    
    def resizeEvent(self, event=None):
        """Méthode exécutée à chaque redimensionnement
        """
        # redimensionne l'image de fond à la nouvelle taille
        self.resizeUi(event.size().width(), event.size().height())   
    
    def resizeUi(self, width=None, height=None):
        """Mise à l'échelle de l'interface
        """
        self.Labels[0].move(int(0.24*width-80/2), int(0.435*height-110/2))
        self.Pumps[0].move(int(0.24*width-50/2), int(0.435*height-50/2))
        self.Labels[1].move(int(0.762*width-80/2), int(0.435*height-110/2))
        self.Pumps[1].move(int(0.762*width-50/2), int(0.435*height-50/2))
        self.Labels[2].move(int(0.65*width-80/2), int(0.635*height+50/2))
        self.Pumps[2].move(int(0.65*width-50/2), int(0.635*height-50/2))
        self.Labels[3].move(int(0.185*width-180/2), int(0.665*height-110/2))
        self.Pumps[3].move(int(0.185*width-50/2), int(0.665*height-50/2))
        self.label.move(int(0.34*width-80/2), int(0.31*height-70/2))
        self.TempRead1.move(int(0.34*width-76/2), int(0.31*height-25/2))
        self.label1.move(int(0.48*width-80/2), int(0.6*height-70/2))
        self.TempRead2.move(int(0.48*width-76/2), int(0.6*height-25/2))
        self.label0.move(int(0.7*width-80/2), int(0.25*height-70/2))
        self.TempSend.move(int(0.7*width-76/2), int(0.25*height-25/2))
    
        #Definition des fonctions de coms avec la carte 
    def send(self, txt):
        print(txt[:-1]) #c'est gentil de montrer la commande avant de l'envoyer
        self.board.write(txt.encode()) #le encode c'est parce que le port série prend des bytes
        
    def read(self):
    		# read instructions from serial
    		while self.board.inWaiting():
    			self.rbuf += self.board.read()
    		if self.rbuf:
    			self.instructions += self.rbuf.split(b'\r')
    			self.rbuf = self.instructions.pop()
    
    		# process instructions
    		while self.instructions:
    			i = self.instructions.pop(0).decode().split(';')
    			if i[0] == 'temp':
    				for j in i[1:]:
    					k,v = j.split('=')
    					if v[0] == 'f':
    						self.state[k] = float(v[1:])
    						print(v[1:])
    					elif v[0] == 'n':
    						self.state[k] = None
 

        #Definition des actions de widget
    def onBtnClicked(self):
        name = self.sender().objectName()
        if self.sender().isChecked():
            self.send(f'@pypl.{name}.open()\r')
        else:
            self.send(f'@pypl.{name}.close()\r')
            
    def setTemperature(self):
        T = float(self.TempSend.value())
        self.send(f'@pypl.TS1.start({T})\r')
        self.send(f'@pypl.TS2.start({T})\r')
            
            
        #Lecture de la température en temps réel
    def update(self):
        self.read()
        self.T1 = self.state['T1']
        self.T2 = self.state['T2']
        self.TempRead1.setValue(self.T1)
        self.TempRead2.setValue(self.T2)
        print(self.T1)
            
     #En cas de fermeture barbare
    def closeEvent(self, event):
         self.send('@pypl.V1.close()\r')
         self.send('@pypl.V2.close()\r')
         self.send('@pypl.V3.close()\r')
         self.send('@pypl.V4.close()\r')
         # self.send('@pypl.TS1.stop()\r')
         # self.send('@pypl.TS2.stop()\r')
         

        
app = QApplication.instance() 
if not app:
    app = QApplication(sys.argv)

fen = Fenetre()
fen.show()

app.exec_()
 
