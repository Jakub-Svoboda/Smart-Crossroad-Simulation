from PyQt5 import QtWidgets, uic, QtCore, QtGui
import PyQt5.QtChart
import pyqtgraph as pg
import sys
import os
import paho.mqtt.client as mqtt
import threading


#global 
mainWindow = None

class Ui(QtWidgets.QMainWindow):
	def __init__(self):
		super(Ui, self).__init__()
		uic.loadUi('ui/ui.ui', self)
		
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')

		self.g1 = pg.PlotWidget()
		self.tab.layout().addWidget(self.g1)

		self.g2 = pg.PlotWidget()
		self.tab_2.layout().addWidget(self.g2)

		Ui.northX = [-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0]
		Ui.northY = [0,0,0,0,0,0,0,0,0,0,0]
		Ui.southX = [-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0]
		Ui.southY = [0,0,0,0,0,0,0,0,0,0,0]

		self.show()

		self.thread = None
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateCharts)

		self.timer.start(200) # Time here is in milliseconds

	def updateCharts(self):
		self.g1.plot(Ui.northX, Ui.northY, pen=pg.mkPen('138', width=5), clear = True)
		self.g2.plot(Ui.southX, Ui.southY, pen=pg.mkPen('138', width=5), clear = True)
		self.timer.start(200) # Time here is in milliseconds


def startMqtt():
	#broker_address="192.168.1.184"
	#broker_address="iot.eclipse.org"
	broker_address="broker.hivemq.com"
	client = mqtt.Client("hmi") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.subscribe("sin/crossroad/north")
	client.subscribe("sin/crossroad/south")
	client.loop_start() #start the loop

	return client

def on_message(client, userdata, message):
	print("message received " ,str(message.payload.decode("utf-8")))
	print("message topic=",message.topic)
	if(message.topic == "sin/crossroad/north"):
		Ui.northY.pop(0)
		Ui.northY.append(int(str(message.payload.decode("utf-8"))))
		print(len(Ui.northY))
	else:
		#target = g2
		pass
	#window.updateCharts()		


def main(args=None):
	#Allow DPI scaling for high resolution displays
	QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
	#Create the main app window from an .ui file
	app = QtWidgets.QApplication(sys.argv)

	global window
	window = Ui()
	#start mqtt
	client = startMqtt()

	app.exec_()

	
if __name__== "__main__":
	main()