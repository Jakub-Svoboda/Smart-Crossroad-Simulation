import os
import sys
import optparse
import paho.mqtt.client as mqtt
import time

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
		#print(step)
		client.publish("sin/crossroad/north", str(step))

		det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
		#for veh in det_vehs:
			#print(veh)

			#traci.vehicle.changeLane(veh, 2, 25)

		# if step == 100:
		#     traci.vehicle.changeTarget("1", "e9")
		#     traci.vehicle.changeTarget("3", "e9")

		step += 1

	traci.close()
	sys.stdout.flush()


def startMqtt():
	#broker_address="192.168.1.184"
	#broker_address="iot.eclipse.org"
	broker_address="broker.hivemq.com"
	#print("creating new instance")
	client = mqtt.Client("simulation") #create new instance
	client.on_message=on_message #attach function to callback
	#print("connecting to broker")
	client.connect(broker_address) #connect to broker
	client.loop_start() #start the loop
	#print("Subscribing to topic","house/bulbs/bulb1")
	client.subscribe("sin/crossroad/north")
	client.subscribe("sin/crossroad/south")
	#print("Publishing message to topic","house/bulbs/bulb1")
	#client.publish("sin/crossroad/north","OFF")
	#time.sleep(4) # wait
	#client.loop_stop() #stop the loop
	return client

def on_message(client, userdata, message):
	print("message received " ,str(message.payload.decode("utf-8")))
	#print("message topic=",message.topic)
	#print("message qos=",message.qos)
	#print("message retain flag=",message.retain)


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