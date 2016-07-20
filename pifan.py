#!/usr/bin/python
# coding: UTF-8
#
# pifan - Controls a fan attached to a Raspberry Pi via a GPIO pin.
#
# Written by Richard Larson
#
# Version 1.0 - 2016/07/19 - First Official Release
#
# Compatibility Note:
# pifan is compatible with both Python2 and Python3, but is set to execute in Python2 because
# it is the version installed on Raspbian by default.  To run via Python3, you will need to
# run the following: "sudo apt-get install python3 python3-rpi.gpio" on your Pi, then update
# the hashbang on line 1 of this file to read "#!/usr/bin/python3".
#
# Licensed via the MIT license: https://github.com/TheRealMrChips/pifan/blob/master/LICENSE
# Latest version available here: https://github.com/TheRealMrChips/pifan
#
# For details on how to wire up a compatible cooling fan, see the README.md in the pifan GitHub repo.
#
import os
import sys
import time
import signal
import argparse
import datetime
import RPi.GPIO as GPIO

# parse the command-line arguments and return our default values...
def parseargs():

	parser=argparse.ArgumentParser(description='PiFan: This command allows you to control a cooling fan attached to a GPIO pin on the raspberry pi. Temperatures are in degrees celcius. GPIO pins are referenced as the physical pin numbers (1-40). In cool mode the app will emit run/stop events to STDOUT with timestamps for each to enable easy logging/monitoring.')

	parser.set_defaults(action='cool')
	parser.add_argument('-a', '--action', 
		type=str,
		choices=['run', 'stop', 'temp', 'cool'], 
		help="Run starts the fan, stop halts it, temp displays the current temperature, cool monitors CPU temperature and turns the fan on or off according to the values of the --onTemp and --offTemp arguments. Default is Cool.")
	
	parser.set_defaults(pin=8)
	parser.add_argument('-p', '--pin',
		type=int,
		help="Sets the GPIO board pin to use for fan control. Default is pin 8.")

	parser.set_defaults(onTemp=60)
	parser.add_argument('-o','--onTemp',
		type=int,
		help="Sets the cool mode temp above which the fan will stay ON. Default is 60°C.")

	parser.set_defaults(offTemp=55)
	parser.add_argument('-f','--offTemp',
		type=int,
		help="Sets the cool mode temp below which the fan will stay OFF. Default is 55°C.")

	parser.set_defaults(checkInterval=60)
	parser.add_argument('-c','--checkInterval',
		type=int,
		help="The number of seconds pifan waits between temperature checks in cool mode. Default is 60.")

	parser.set_defaults(exitAction='stop')
	parser.add_argument('-x', '--exitAction', 
		type=str,
		choices=['run', 'stop'], 
		help="Sets the state the fan will be left in upon exit of cool mode. Default is Stop.")

	parser.set_defaults(utcTime=False)
	parser.add_argument('-u','--utcTime',
		action="store_true",
		help="Use UTC time on status timestamps. Default is local time.")

	parser.set_defaults(verbose=False)
	parser.add_argument('-v','--verbose',
		action="store_true",
		help="Tells cool mode to log status every interval regardless of fan-state changes.")

	args=parser.parse_args()
	return args

# get integral value of current cpu temperature...
def getCPUTempCelcius():
	temp = os.popen("vcgencmd measure_temp").readline()
	temp = temp.replace("temp=","").replace("'C\n","")
	return int(float(temp))

# get current date/time as an ISO8601 formatted string...
def getCurrentDateTimeISO8601(utc=True):
	if utc:
		return datetime.datetime.utcnow().isoformat()
	else:
		return datetime.datetime.now().isoformat()

# emit a status record...
def emitStatus(fanState,currentTemp):
	printItems=[]
	printItems.append(getCurrentDateTimeISO8601())
	printItems.append(str(currentTemp))
	printItems.append(fanState)
	output = '\t'.join(printItems)
	print(output)
	sys.stdout.flush()

# turn the fan ON or OFF for a specified GPIO pin...
def fanControl(pin,state):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)
	GPIO.setup(pin, GPIO.OUT)
	if state == _FANON:
		GPIO.output(pin, 1)
	elif state == _FANOFF:
		GPIO.output(pin, 0)

# cleanup routine that executes at exit of application...
def cleanupBeforeExit(signum, frame):

	# always leave the fan in the desired exit mode (run or stop)...
	finalState = _FANOFF if _args.exitAction == 'stop' else _FANON
	fanControl(_args.pin, finalState)
	
	# determine reason we stopped...
	stoppedBy = 'by-user' if signum == 0 else 'by-sigterm'
	emitStatus('cooling-mode: ended-' + stoppedBy, getCPUTempCelcius())
	sys.exit(0)

# cooling routine that monitors CPU temps and automates fan control accordingly...
def runCooling(args):

	# display a cool-mode status so users can log when app started/stopped...
	emitStatus('cooling-mode: running', getCPUTempCelcius())

	# set up system hooks to handle termination signals gracefully by running cleanup...
	signal.signal(signal.SIGTERM, cleanupBeforeExit)

	# always start with fan OFF...
	args.fanState = _FANOFF
	fanControl(args.pin, args.fanState)

	# loop forever, testing and changing fan state as we go...
	try:
		while True:
	
			# obtain the current CPU temperature...
			args.currentTemp = getCPUTempCelcius()
	
			# caclulate the action we want to take with the fan...
			desiredFanState = _FANUNCHANGED
			if (args.currentTemp > args.onTemp):
				desiredFanState = _FANON
			elif (args.currentTemp < args.offTemp):
				desiredFanState = _FANOFF

			# only apply our action if it differs from the current state...
			if desiredFanState != _FANUNCHANGED:	
				fanControl(args.pin, desiredFanState)
				args.fanState = desiredFanState
				emitStatus(args.fanState, args.currentTemp)
			elif args.verbose == True:
				emitStatus(args.fanState, args.currentTemp)

			# sleep a bit before doing it all again...
			time.sleep(args.checkInterval)

	# handle ctrl-c interuptions:
	except KeyboardInterrupt:
		cleanupBeforeExit(0,0)
		pass

# take appropriate action based on the command arguments...
def processAction(args):

	if args.action == 'run':
		fanControl(args.pin, _FANON)

	elif args.action == 'stop':
		fanControl(args.pin, _FANOFF)

	elif args.action == 'temp':
		currentTemp = getCPUTempCelcius()
		print(currentTemp)
		sys.stdout.flush()

	elif args.action == 'cool':
		runCooling(args)

#**********
#** MAIN **
#**********

# generate runtime variables based on the parsed user intent...
_FANON = 'running'
_FANOFF = 'idle'
_FANUNCHANGED = 'unchanged'
_args=parseargs()

# and execute the given action...
processAction(_args)
