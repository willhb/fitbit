# 	(c)2014 William Breidenthal
# 	willhb@gmail.com
#	http://www.willhb.com
# 	About: Grabs step count and goal from the fitbit API and send the completion percent out over a serial port.
#			The script will store the OAuth keys/secrests in a config.ini file. 
#	Requires:
#		 Python-Fitbit: http://python-fitbit.readthedocs.org/en/latest/
#		 PySerial: http://pyserial.sourceforge.net
#	Todo: Error handling in some form			

import fitbit
import ConfigParser
import webbrowser
import sys
import time
import serial

parser = ConfigParser.SafeConfigParser()
parser.read('./config.ini')
consumer_key = parser.get('OAuth Parameters', 'CONSUMER_KEY')
consumer_secret = parser.get('OAuth Parameters', 'CONSUMER_SECRET')
serial_port = parser.get('Serial Parameters', 'SERIAL_PORT')
baud_rate = int(parser.get('Serial Parameters', 'BAUD_RATE'))
timeout = int(parser.get('Serial Parameters', 'TIMEOUT'))
update_rate = int(parser.get('Fitbit Parameters', 'UPDATE_RATE'))


if update_rate > 150:
	update_rate = 150
	print "Max polling rate for Fitibt API is 150/hour."

previous = 0

#serialport = raw_input("Enter serial port:")
ser = serial.Serial(serial_port, baud_rate, timeout=timeout)

#Get the application OAuth keys from a config file
while 1:

	user_key = parser.get('OAuth Parameters', 'USER_KEY')
	user_secret = parser.get('OAuth Parameters', 'USER_SECRET')
	user_id = parser.get('OAuth Parameters', 'USER_ID')
	
	if (user_id == '') or (user_id == '0'):
		#we don't have a user
		print "No user. Authenticating with Fitbit..."
	
		#Configure the OAuth client
		client = fitbit.FitbitOauthClient(consumer_key, consumer_secret) 
	
		#Get a token to use
		token = client.fetch_request_token()
	
		#Get the URL to authorize the current user
		url = client.authorize_token_url()
	
		#Open the default browser and then prompt for the user pin
		webbrowser.open(url)
	
		pin = raw_input("Please enter your pin: ")
	
		access = client.fetch_access_token(verifier=pin, token=token)
	
		parser.set('OAuth Parameters', 'USER_ID', client.user_id)
		parser.set('OAuth Parameters', 'USER_SECRET', client.resource_owner_secret)
		parser.set('OAuth Parameters', 'USER_KEY', client.resource_owner_key)
		fp = open("./config.ini",'w')
		parser.write(fp)
		fp.close
	else:
		client = fitbit.FitbitOauthClient(consumer_key, consumer_secret, resource_owner_key=user_key, resource_owner_secret=user_secret, user_id=user_id)
	
	auth_client = fitbit.Fitbit(consumer_key, consumer_secret, user_key=user_key, user_secret=user_secret)
	auth_client.client = client
	
	profile = auth_client.user_profile_get()
	
	prompt = raw_input("Are you " + profile['user']['displayName'] + "?[y]")
	
	if (prompt == 'yes') or (prompt == 'y') or (prompt == ''):
		print "Hi! Running step counter display. CTRL-C to Exit."
		print "Updating " + str((60*60)/update_rate) + " times per hour."
		break
	else:
		print "Clearing configuration, please re-run."
		parser.set('OAuth Parameters', 'USER_ID', '0')
		parser.set('OAuth Parameters', 'USER_SECRET', '0')
		parser.set('OAuth Parameters', 'USER_KEY', '0')
		fp = open("./config.ini",'w')
		parser.write(fp)
		fp.close

#loop forever and print echo our daily step goal progress
while 1:

	date = time.strftime("%Y-%m-%d")

	current_activities = auth_client._COLLECTION_RESOURCE('activities',date=date)

	goal = current_activities['goals']['steps']

	steps = current_activities['summary']['steps']

	progress = int((float(steps)/float(goal))*1000)

#only print updates when we have done some activity
	if progress != previous:
		previous = progress
		print time.strftime("%H:%m - ") + str(float(progress)/10.0) + "%"
		# At midnight the counter will resent, don't update until it is a reasonable hour!
		if time.strftime("%H") > 7:
			ser.write(str(progress) + "\n\r")

	#60 seconds * 60 minutes in an hour / update rate
	time.sleep(int((60*60)/update_rate))

