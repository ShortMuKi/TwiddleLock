import pygame
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import time
import os
import spidev
import sys
import subprocess as sp

GPIO.setmode(GPIO.BCM)
#pygame.mixer.init()
#pygame.mixer.load("Apple Pay Succes Sound Effect.wav")

#pin Definition
SPICLK = 11
SPIMISO = 9 
SPIMOSI = 10
SPICS = 8

# pin numbers switch
start = 19
locked = 26
unlocked = 21

#SET ADC Pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

#Button pin setups
GPIO.setup(start,   GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(locked,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(unlocked,GPIO.IN, pull_up_down=GPIO.PUD_UP)

mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK,   cs=SPICS,   mosi=SPIMOSI,  miso=SPIMISO)

#Global Variables
dur = [4]*16;
code =[1,1,0];
times = [2000,2000,2000]
dir = [4]*16;
values = [0]*8
count = 0;
master =[2]
duration = 0;
change  = 0.0;
pre_pot = 0.0;
place = 3
stop =0
sercure  = 1;
# 0 is a left movement 
# 1 is a right movement

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

	if (change > 0.01):
		if (master[(len(master)-1)]==0):
			master.append(place)
			place =place+1
#		print("right")
		master.append(1)
		count = 0

	elif (change <-0.01):
		if (master[(len(master)-1)]==1):
			master.append(place)
			place =place+1
#		print("left")
		master.append(0)
		count = 0

	elif (count ==10):
		master.append(place)
		place = place + 1;
		count =count +1

	elif (change<0.05 or change >-0.05 ):
#		print("no change")
		count = count+1
def s(channel):
	global begin
	begin = 1

GPIO.add_event_detect(start, GPIO.FALLING, callback=s, bouncetime=200)

try:
	begin = 0
	while (begin == 0):
		time.sleep(0.01)
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
				print(dir)
				print(dur)
				sorte = sorty(dur)
				print(sorte)
				break
				if (sercure ==1):
					if (dir[(len(dir)-1)] == code[2] and  dir[(len(dir)-2)] == code[1] and dir[(len(dir)-3)] == code[0] and
					round((dur[(len(dur)-1)]/1000),0)*1000 == times[2] and  round((dur[(len(dur)-2)]/1000),2)*1000 == times[1] and round((dur[(len(dur)-3)]/1000),2)*1000 == times[0]):
						print('yay')
						dir = [4]*16;
						dur = [0]*16;
					else :
						print ('Failed')
						dir = [4]*16;
						dur = [0]*16;
				elif (secure ==0):
					
		time.sleep(0.1)
finally:
    GPIO.cleanup()
