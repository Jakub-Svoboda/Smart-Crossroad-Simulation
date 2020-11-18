from PyQt5 import QtWidgets, uic, QtCore, QtGui
import PyQt5.QtChart
import pyqtgraph as pg
import sys
import os
import paho.mqtt.client as mqtt
import threading

client = None

class Ui(QtWidgets.QMainWindow):
	def __init__(self):
		super(Ui, self).__init__()
		uic.loadUi('ui/ui.ui', self)
		self.setWindowIcon(QtGui.QIcon('ui/icon.ico'))
		
		pg.setConfigOption('background', 'w')
		pg.setConfigOption('foreground', 'k')

		self.g1 = pg.PlotWidget()
		self.tab.layout().addWidget(self.g1)

		self.g2 = pg.PlotWidget()
		self.tab_2.layout().addWidget(self.g2)

		self.g1.setXRange(-100, 0, padding=0.00)
		self.g2.setXRange(-100, 0, padding=0.00)
		self.g1.setYRange(0, 80, padding=0.02)
		self.g2.setYRange(0, 80, padding=0.02)
		styles = {'color':'r', 'font-size':'13px'}
		self.g1.setLabel('left', 'Occupancy', **styles)
		self.g1.setLabel('bottom', 'Time (Step)', **styles)
		self.g2.setLabel('left', 'Occupancy', **styles)
		self.g2.setLabel('bottom', 'Time (Step)', **styles)
		self.g1.showGrid(x=True, y=True)
		self.g2.showGrid(x=True, y=True)

		Ui.northX = [-200,-190,-180,-170,-160,-150,-140,-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0]
		Ui.northY = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		Ui.southX = [-200,-190,-180,-170,-160,-150,-140,-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0]
		Ui.southY = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		self.comboBox.currentIndexChanged.connect(self.northChanged)
		self.comboBox_2.currentIndexChanged.connect(self.southChanged)
		self.show()

		self.thread = None
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.updateCharts)

		self.timer.start(200) # Time here is in milliseconds

	def updateCharts(self):
		self.g1.plot(Ui.northX, Ui.northY, fillBrush=pg.mkBrush(0, 0, 255, 90), fillLevel = 0, pen=pg.mkPen('138', width=5), clear = True)
		self.g2.plot(Ui.southX, Ui.southY, fillBrush=pg.mkBrush(0, 0, 255, 90), fillLevel = 0, pen=pg.mkPen('138', width=5), clear = True)


		self.timer.start(200) # Time here is in milliseconds


	def northChanged(self, value):
		if value == 0:
			client.publish("sin/crossroad/setNorth", "northBalanced")
		elif value == 1:
			client.publish("sin/crossroad/setNorth", "northNSBoost")
		elif value == 2:
			client.publish("sin/crossroad/setNorth", "northEWBoost")
		elif value == 3:
			client.publish("sin/crossroad/setNorth", "northNSOnly")
		elif value == 4:
			client.publish("sin/crossroad/setNorth", "northEWOnly")	

	def southChanged(self, value):
		if value == 0:
			client.publish("sin/crossroad/setSouth", "southBalanced")
		elif value == 1:
			client.publish("sin/crossroad/setSouth", "southNEBoost")
		elif value == 2:
			client.publish("sin/crossroad/setSouth", "southNWBoost")
		elif value == 3:
			client.publish("sin/crossroad/setSouth", "southEWBoost")	
		elif value == 4:
			client.publish("sin/crossroad/setSouth", "southNEOnly")
		elif value == 5:
			client.publish("sin/crossroad/setSouth", "southNWOnly")	
		elif value == 6:
			client.publish("sin/crossroad/setSouth", "southEWOnly")		

def startMqtt():
	global client
	broker_address="broker.hivemq.com"
	client = mqtt.Client("hmi") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.subscribe("sin/crossroad/north")
	client.subscribe("sin/crossroad/south")
	client.loop_start() #start the loop

	return client

def on_message(client, userdata, message):
	#print("message received " ,str(message.payload.decode("utf-8")))
	if(message.topic == "sin/crossroad/north"):
		Ui.northY.pop(0)
		Ui.northY.append(float(str(message.payload.decode("utf-8"))))
	else:
		Ui.southY.pop(0)
		Ui.southY.append(float(str(message.payload.decode("utf-8"))))


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