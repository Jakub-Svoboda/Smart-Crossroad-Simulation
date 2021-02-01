# Author: Jakub Svoboda
# Date: 23.11.2020
# Email: xsvobo0z@stud.fit.vutbr.cz, svo.jakub95@gmail.com
#
# This script runs a simulation of a traffic crossroad in SUMO/TraCI


import os
import sys
import optparse
import paho.mqtt.client as mqtt
import time

NS = False
EW = False

# import  python modules from the $SUMO_HOME/tools directory
# source: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci


def get_options():
	opt_parser = optparse.OptionParser()
	opt_parser.add_option("--nogui", action="store_true", default=False, help="Run the sim without GUI.")
	options, _ = opt_parser.parse_args()
	return options


# contains TraCI control loop
def run(client):
	step = 0
	while traci.simulation.getMinExpectedNumber() > 0: 	#simulation end condition
		traci.simulationStep()							#time advance
		trafficNNS = (traci.lanearea.getLastStepOccupancy("NNS") + traci.lanearea.getLastStepOccupancy("NNS2")) / 2 #North South has two detection zones, get average
		trafficNEW = (traci.lanearea.getLastStepOccupancy("NEW") + traci.lanearea.getLastStepOccupancy("NEW2")) / 2 #East West
		client.publish("sin/crossroad/north/occupancy", str(trafficNNS - trafficNEW))								#send to controller
		if(EW == False and NS == False):	#Set program to balanced
			traci.trafficlight.setProgram("n5", "northBalanced")
		elif(EW == True):					#Allow north/south 
			traci.trafficlight.setProgram("n5", "northEWOnly")
		elif(NS == True):					#allow east/west
			traci.trafficlight.setProgram("n5", "northNSOnly")

		client.publish("sin/currentProgram",traci.trafficlight.getProgram("n5"))

		step += 1

	traci.close()
	sys.stdout.flush()


def startMqtt():
	broker_address="broker.hivemq.com"
	#broker_address="localhost"
	client = mqtt.Client("simulation") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.loop_start() #start the loop
	client.subscribe("sin/crossroad/setNNS")
	client.subscribe("sin/crossroad/setNEW")
	client.subscribe("sin/currentProgram")
	return client

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	if message.topic == "sin/crossroad/setNNS":
		global NS
		if msg == "TRUE":
			NS = True
		else:
			NS = False	
	elif message.topic == "sin/crossroad/setNEW":		
		global EW
		if msg == "TRUE":
			EW = True
		else:
			EW = False



# main entry point
if __name__ == "__main__":
	options = get_options()

	# check binary
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')

	client = startMqtt()	

	# traci starts sumo as a subprocess and then this script connects and runs
	traci.start([sumoBinary, "-c", "simulation/sin.sumocfg", "--tripinfo-output", "simulation/log.xml"])
	run(client)