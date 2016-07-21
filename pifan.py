#!/usr/bin/python
# coding: UTF-8

""" 
pifan - Controls a fan attached to a Raspberry Pi via a GPIO pin.

Written by Richard Larson

Version 2.0 - 2016/07/21 - Second Official Release (Many Changes from 1.0!!!)

Compatibility Note:

	pifan is compatible with both Python2 and Python3, but is set to execute in Python2 because
	it is the version installed on Raspbian by default.  To run via Python3, you will need to
	run the following: "sudo apt-get install python3 python3-rpi.gpio" on your Pi, then update
	the hashbang on line 1 of this file to read "#!/usr/bin/python3".

Licensed via the MIT license: https://github.com/TheRealMrChips/pifan/blob/master/LICENSE
Latest version available here: https://github.com/TheRealMrChips/pifan
Change log is available here: https://github.com/TheRealMrChrips/blob/master/CHANGELOG

For details on how to wire up a compatible cooling fan, see the README.md in the pifan GitHub repo.
"""

import os
import sys
import time
import signal
import argparse
import datetime
import RPi.GPIO as GPIO

# define global constants...
_FANON = 'cooling'
_FANOFF = 'stopped'
_FANUNCHANGED = 'unchanged'
_TEMPERATURECHECK = 'current-temperature'


# parse the command-line arguments and return our default values...
def parseargs():

	parser=argparse.ArgumentParser(description='PiFan: This command allows you to control a cooling fan attached to a GPIO pin on the raspberry pi. Temperatures are in degrees celcius. GPIO pins are referenced as the physical pin numbers (1-40). In cool mode the app will emit run/stop events to STDOUT with timestamps for each to enable easy logging/monitoring.')

	parser.set_defaults(mode='temp')
	parser.add_argument('-m', '--mode', 
		type=str,
		choices=['run', 'stop', 'temp', 'cron', 'daemon'], 
		help="Run mode starts the fan, stop mode halts it, temp mode just outputs the current temperature, cron mode turns the fan on or off according to the values of the --onTemp and --offTemp arguments and is designed to make fan control easy in cron scripts (hence the name). Daemon mode is the same as cron mode, but runs forever until the app is terminated. Default is 'temp' mode.")
	
	parser.set_defaults(pin=8)
	parser.add_argument('-p', '--pin',
		type=int,
		help="Sets the GPIO board pin to use for fan control. Default is pin 8.")

	parser.set_defaults(onTemp=60.0)
	parser.add_argument('-o','--onTemp',
		type=float,
		help="Sets the cron & daemon mode temperature above which the fan will be turned ON. Default is 60°C.")

	parser.set_defaults(offTemp=55.0)
	parser.add_argument('-f','--offTemp',
		type=float,
		help="Sets the cron & daemon mode temperature below which the fan will by turned OFF when it is already ON. Default is 55°C.")

	parser.set_defaults(checkInterval=60)
	parser.add_argument('-c','--checkInterval',
		type=int,
		help="The number of seconds pifan waits between temperature checks in daemon mode. Default is 60.")

	parser.set_defaults(exitAction='stop')
	parser.add_argument('-x', '--daemonExitAction', 
		type=str,
		choices=['run', 'stop'], 
		help="Sets the state the fan will be left in upon exit of daemon mode. Default is Stop.")

	parser.set_defaults(utcTime=False)
	parser.add_argument('-u','--utcTime',
		action="store_true",
		help="Use UTC time on status timestamps. Default is local time.")

	args=parser.parse_args()
	return args


# get integral value of current cpu temperature...
def getCPUTempCelcius():

	temp = os.popen("vcgencmd measure_temp").readline()
	temp = temp.replace("temp=","").replace("'C\n","")
	return float(temp)


# get current date/time as an ISO8601 formatted string...
def getCurrentDateTimeISO8601(utc=False):

	if utc:
		return datetime.datetime.utcnow().isoformat()
	else:
		return datetime.datetime.now().isoformat()


# emit a status record...
def emitStatus(statusMsg,currentTemp):

	printItems=[]
	printItems.append(getCurrentDateTimeISO8601(_args.utcTime))
	printItems.append(str(currentTemp))
	printItems.append(statusMsg)
	output = '\t'.join(printItems)
	print(output)
	sys.stdout.flush()


# turn the fan ON or OFF for a specified GPIO pin...
def fanControl(pin,state):

	# only take action if needed...
	if state != _FANUNCHANGED:

		# set up GPIO pin details...
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(pin, GPIO.OUT)

		# and set high for ON, and low for OFF...
		if state == _FANON:
			GPIO.output(pin, 1)
		elif state == _FANOFF:
			GPIO.output(pin, 0)


# cleanup routine that executes when application is terminating from daemon mode...
def cleanupBeforeExit(signum, frame):

	# always leave the fan in the desired exit mode (run or stop)...
	finalState = _FANOFF if _args.exitAction == 'stop' else _FANON
	fanControl(_args.pin, finalState)
	GPIO.cleanup()
	
	# determine reason we stopped...
	stoppedBy = 'by-user' if signum == 0 else 'by-sigterm'
	emitStatus('daemon-cooling-mode: ended-' + stoppedBy, getCPUTempCelcius())

	# and exit cleanly...
	sys.exit(0)


# apply temperature-based rules to turn fan on or off...
def applyCoolingRules(args):

	# obtain the current CPU temperature...
	args.currentTemp = getCPUTempCelcius()

	# caclulate the action we want to take with the fan...
	desiredFanState = _FANUNCHANGED
	if (args.currentTemp > args.onTemp):
		desiredFanState = _FANON
	elif (args.currentTemp < args.offTemp):
		desiredFanState = _FANOFF

	# apply our changes...
	fanControl(args.pin, desiredFanState)
	args.fanState = desiredFanState

	# and log our results...
	emitStatus(args.fanState, args.currentTemp)


# cooling routine that monitors CPU temps and automates fan control accordingly...
def runDaemon(args):

	# set up system hook to handle termination signals gracefully by running cleanup...
	signal.signal(signal.SIGTERM, cleanupBeforeExit)

	# display a cool-mode status so users can see when app started/stopped...
	emitStatus('daemon-cooling-mode: started', getCPUTempCelcius())

	# always start with fan OFF...
	args.fanState = _FANOFF
	fanControl(args.pin, args.fanState)

	# daemon-loop until Ctrl-C or SIGTERM recieved...
	try:
		while True:
	
			# test and set fan state based on temperature...
			applyCoolingRules(args)

			# sleep a bit before doing it all again...
			time.sleep(args.checkInterval)

	# handle ctrl-c interuptions:
	except KeyboardInterrupt:
		cleanupBeforeExit(0,0)
		pass

# take appropriate action based on the command arguments...
def processAction(args):

	# 'run' mode - turn the fan on...
	if args.mode == 'run':
		fanControl(args.pin, _FANON)

	# 'stop' mode - turn the fan off...
	elif args.mode == 'stop':
		fanControl(args.pin, _FANOFF)

	# 'temp' mode - return the current temp (no fan changes in this mode)...
	elif args.mode == 'temp':
		emitStatus(_TEMPERATURECHECK, getCPUTempCelcius())

	# 'cool' mode - adjust fan state (on/off/unchanged) based on current temperature, then exit...
	elif args.mode == 'cron':
		applyCoolingRules(args)

	# 'daemon' mode - monitor temperature and adjust fan state continuously until terminated...
	elif args.mode == 'daemon':
		runDaemon(args)

""" 
**************************
** MAIN APP STARTS HERE **
**************************
"""

# generate runtime variables from CLI options and then execute the desired application mode...
_args=parseargs()
processAction(_args)
