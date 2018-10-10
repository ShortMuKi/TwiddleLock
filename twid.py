import RPi.GPIO as GPIO
import Adafruit_MCP3008
import time
import os
import spidev
import sys
import subprocess as sp

GPIO.setmode(GPIO.BCM)

#pin Definition

SPICLK = 11
SPIMISO = 9 
SPIMOSI = 10
SPICS = 8

# pin numbers switch

start = 19

#SET ADC Pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

#Button pin setups
GPIO.setup(start, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK,   cs=SPICS,   mosi=SPIMOSI,  miso=SPIMISO)

#Global Variables
#int log[16]
#int dir[16]
values = [0]*8

# 0 is a left movement 
# 1 is a right movement
def potconvert(Vals,dec):
	volts = (Vals*3.3/float(1023))
	volts = round(volts,dec)
	return volts
def direction (change):
	if (change > 0):
		print("right")
	elif (change <0):
		print("left")
		
	
try:
  pot = 0
  while True:
      values[0] = mcp.read_adc(0)
      pre_pot = pot
      pot = potconvert(values[0],2)
      change = pot - pre_pot; 
      print(pot);
      print(pre_pot);
      direction(change);
	
      time.sleep(1);
			

	
finally:
    GPIO.cleanup()
