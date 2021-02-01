# Author: Jakub Svoboda
# Date: 23.11.2020
# Email: xsvobo0z@stud.fit.vutbr.cz, svo.jakub95@gmail.com
#
# This script runs the human-machine interface for the controlled crossroad


from PyQt5 import QtWidgets, uic, QtCore, QtGui
import pyqtgraph as pg
import sys
import os
import paho.mqtt.client as mqtt
import threading

client = None
label = None

class Ui(QtWidgets.QMainWindow):
	def __init__(self):
		super(Ui, self).__init__()
		uic.loadUi('ui/ui.ui', self)
		self.setWindowIcon(QtGui.QIcon('ui/icon.ico'))
		
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')

		self.g1 = pg.PlotWidget()
		self.frame_2.layout().addWidget(self.g1)

		global label
		label = self.label

		self.g1.setXRange(-100, 0, padding=0.01)
		self.g1.setYRange(-50, 50, padding=0.02)
		styles = {'color':'r', 'font-size':'13px'}
		self.g1.setLabel('left', 'Occupancy (North-South v East-West)', **styles)
		self.g1.setLabel('bottom', 'Time (Step)', **styles)
		self.g1.showGrid(x=True, y=True)

		Ui.northX = [-200,-190,-180,-170,-160,-150,-140,-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0]
		Ui.northY = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		self.show()

		self.thread = None
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateCharts)

		self.timer.start(200) # Time here is in milliseconds

	def updateCharts(self):

		self.g1.plot(Ui.northX, Ui.northY, fillBrush=pg.mkBrush(0, 0, 255, 90), fillLevel = 0, pen=pg.mkPen('138', width=5), clear = True)
		self.g1.plot([i for i in range(-200, 10, 10)], [20 for y in range(-200, 10, 10)], pen=pg.mkPen('r', width=2))
		self.g1.plot([i for i in range(-200, 10, 10)], [-20 for y in range(-200, 10, 10)], pen=pg.mkPen('r', width=2))
		self.timer.start(200) # Time here is in milliseconds


	def northChanged(self, value):
		pass

	

def startMqtt():
	global client
	broker_address="broker.hivemq.com"
	#broker_address="localhost"
	client = mqtt.Client("hmi") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.subscribe("sin/crossroad/north/occupancy")
	client.subscribe("sin/currentProgram")
	client.loop_start() #start the loop
	return client

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	#print("message received " , msg + " in topic " + message.topic) 
	if message.topic == "sin/crossroad/north/occupancy":
		Ui.northY.pop(0)
		Ui.northY.append(float(str(message.payload.decode("utf-8"))))
	elif message.topic == "sin/currentProgram":
		if label is not None:
			if msg == "northBalanced":
				label.setText("Balanced")
			elif msg == "northNSOnly":
				label.setText("North-South Only")
			elif msg == "northEWOnly":
				label.setText("East-West Only")	
			else:
				label.setText(msg)	



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