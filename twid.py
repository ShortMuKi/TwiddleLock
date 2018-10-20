import pygame
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import time
import os
import spidev
import sys
import subprocess as sp

pygame.init()

GPIO.setmode(GPIO.BCM)

#pin Definition
SPICLK = 11
SPIMISO = 9 
SPIMOSI = 10
SPICS = 8

# pin numbers 
start = 19
locked = 26
unlocked = 21
sec = 27

#SET ADC Pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

#Button pin setups
GPIO.setup(start,   GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(sec,  GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Ouput Pins
GPIO.setup(locked,  GPIO.OUT)
GPIO.setup(unlocked,GPIO.OUT)

mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK,   cs=SPICS,   mosi=SPIMOSI,  miso=SPIMISO)

#Global Variables
dur = [9]*16;
code =[1,1,0,0,0,1,1,0,0,1,1,1,1,1,0,0];
times = [2000,2000,2000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
dir = [9]*16;
values = [0]*8
count = 0;
master =[2]
duration = 0;
change  = 0.0;
pre_pot = 0.0;
place = 3
stop =0
secure  = 1;
sens = 0.02
# 0 is a left movement 
# 1 is a right movement

# sort function
def sorty(list):
	for z in range((len(list))-1,0,-1):
		max=0
		for p in range(1,z+1):
			if list[p] > list[max]:
				max = p
		solong = list[z]
		list[z] = list[max]
		list[max] = solong
	return list

def potconvert(Vals,dec):
	volts = (Vals*3.3/float(1023))
	volts = round(volts,dec)
	return volts
def getpot():
	global values
	global change
	global pot
	global pre_pot
	pre_pot = pot; 
	values[0] = mcp.read_adc(0);
	pot = potconvert(values[0],2);
	change = pot-pre_pot;
#	print (" this is change",change)
	return change

def direction (change):
	global place
	global count
	global dir

	if (change > sens):					#right
		if (master[(len(master)-1)]==0):
			master.append(place)
			place =place+1
		master.append(1)
		count = 0

	elif (change <-sens):					#left
		if (master[(len(master)-1)]==1):
			master.append(place)
			place =place+1
		master.append(0)
		count = 0

	elif (count ==10):					# 1 second timer for new entry
		master.append(place)
		place = place + 1;
		count =count +1

	elif (change<sens or change >-sens):			# No Change
		count = count+1


def compare():
	global secure
	global dur
	global code
	global times
	global dir
	rounded = [0]*len(times)
	timesR = [0]*len(times)
	correct = 0
	Tcorrect = 0
	sorted_rounded = []
	sorted_time = []
	sorted_timeR = []
	for m in range (0,len(times)-1):
		rounded[m] = (round(dur[(len(dur)-1-m)]*1000,0)/1000)
		timesR[m] = (round(times[m]*1000,0)/1000)
	rounded.reverse()
	if secure == 1:
		for  k in range(0,len(code)-1):
			if code[k] == dir[(16-len(code)+k)]:
				correct  = correct + 1
			if timesR[k] == rounded[k]:
				Tcorrect = Tcorrect + 1
		if ((Tcorrect + correct) == 2*len(code)):
			return 1
		else:
			return 0
	if secure == 0:
		sorted_timeR = sorty(timesR)
		sorted_rounded = sorty(rounded)
		for k in range (0,len(code)-1):
			if sorted_time[k] == sorted_rounded[k]:
				correctT = correcT + 1
		if correctT ==len(code):
			return 1
		else:
			return 0

# interrupt to change begin variable
def s(channel):
	global begin
	begin = 1

#interrupt to change secure and unsecure mode
def change_sec(channel):
	global secure
	if ( secure == 1):
		secure = 0
		print("You are now in unsecure mode")
	elif (secure == 0):
		secure = 1
		print("You are now in secure mode")

GPIO.add_event_detect(start, GPIO.FALLING, callback=s, bouncetime=200)
GPIO.add_event_detect(sec, GPIO.FALLING, callback=change_sec, bouncetime=200)

try:
	while(1):
		GPIO.output(locked,1)
		master =[2]
		place = 3
		begin = 0
#		print(begin)
		print("Press to start")
		while (begin == 0):
			time.sleep(0.01)
			stop = 0;
#		print(begin)
#		print(dur)
#		print(dir)
		print("enter your Passcode")
		pot = 0.0
		while (stop ==0):
			getpot()
			direction(change);
			if (count == 20):
				stop = 1
			#print(master)
				if(stop ==1):
					for i in range (2,place-1):
						start = master.index(i)
						finish = master.index(i+1)
						duration = (finish -start)*100
						dur=dur[1:]
						dur.append(duration)
						val = master[(finish -1)]
						dir = dir[1:]
						dir.append(val)
					#print(dir)
					#print(dur)
					sorte = sorty(dur)
					#print(sorte)
					#break
#					if (secure == 1):
#						rounded = [round((dur[(len(dur)-3)]/1000),0)*1000,round((dur[(len(dur)-2)]/1000),0)*1000,round((dur[(len(dur)-1)]/1000),0)*1000]
#						#print (rounded)
#						if( dir[(len(dir)-1)] == code[2] and  dir[(len(dir)-2)] == code[1] and dir[(len(dir)-3)] == code[0] and
#						round((dur[(len(dur)-1)]/1000),0)*1000 == times[2] and  round((dur[(len(dur)-2)]/1000),0)*1000 == times[1] and round((dur[(len(dur)-3)]/1000),0)*1000 == times[0] ):
#							#print(secure)

					check = compare()
					if (check == 1):
						print('yay')
						pygame.mixer.music.load("hap")
						pygame.mixer.music.play()
						dir = [4]*16
						dur = [0]*16
						master = [2]
						GPIO.output(locked,0)
						GPIO.output(unlocked,1)
						time.sleep(2)
						GPIO.output(unlocked,0)
						GPIO.output(locked,1)

					else :
							#print(secure)
						print ('Failed')
						pygame.mixer.music.load("sad")
						pygame.mixer.music.play()
						dir = [4]*16;
						master = [2]
						dur = [0]*16;

#					elif(secure == 0):
#						dur = sorte
#						combcode = sorty(times)
#						if ( round((dur[(len(dur)-1)]/1000),0)*1000 == combcode[2] and  round((dur[(len(dur)-2)]/1000),0)*1000 == combcode[1] and round((dur[(len(dur)-3)]/1000),0)*1000 == combcode[0]):
#							#print(secure)
#							print('yay')
#							pygame.mixer.music.load("hap")
#							pygame.mixer.music.play()
#							dir = [4]*16;
#							dur = [0]*16;
#							master = [2]
#							GPIO.output(locked,0)
#							GPIO.output(unlocked,1)
#							time.sleep(2)
#							GPIO.output(unlocked,0)
#							GPIO.output(locked,1)
#						else :
#							#print(secure)
#							print ('Failed')
#							pygame.mixer.music.load("sad")
#							pygame.mixer.music.play()
#							dir = [9]*16;
#							dur = [9]*16;
#							master=[2]

			time.sleep(0.1)
		stop = 0
finally:
    GPIO.cleanup()
