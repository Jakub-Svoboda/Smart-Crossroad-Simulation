import os
import sys
import optparse
import paho.mqtt.client as mqtt
import time

northProgram = "northBalanced"
southProgram = "southBalanced"

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

		traffic = traci.lanearea.getLastStepOccupancy("det_1")
		client.publish("sin/crossroad/north", str(traffic))
		traffic2 = traci.lanearea.getLastStepOccupancy("det_2")
		client.publish("sin/crossroad/south", str(traffic2))
		traci.trafficlight.setProgram("n5", northProgram)
		traci.trafficlight.setProgram("n2", southProgram)
		step += 1

	traci.close()
	sys.stdout.flush()


def startMqtt():
	broker_address="broker.hivemq.com"
	client = mqtt.Client("simulation") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.loop_start() #start the loop
	client.subscribe("sin/crossroad/north")
	client.subscribe("sin/crossroad/south")
	client.subscribe("sin/crossroad/setNorth")
	client.subscribe("sin/crossroad/setSouth")
	return client

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	if message.topic == "sin/crossroad/setNorth":
		global northProgram
		northProgram = msg
	elif message.topic == "sin/crossroad/setSouth":
		global southProgram
		southProgram = msg


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