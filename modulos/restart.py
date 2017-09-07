#!/usr/bin/python3
import commands
import time

def restart():
	# os.system("ps -ef | grep bot.py | awk '{print $2}' | xargs sudo kill")
	# time.sleep(2)
	os.system('sudo python3 /home/pi/bot/bot.py')
	result = commands.getoutput('sudo python3 /home/pi/bot/bot.py')
	
restart()
