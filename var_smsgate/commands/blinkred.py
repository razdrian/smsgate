#!/usr/bin/python

LEDRED=40
import sys
import RPi.GPIO as GPIO
from time import *

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LEDRED, GPIO.OUT)


GPIO.output(LEDRED, GPIO.HIGH)
sleep(0.2)
GPIO.output(LEDRED, GPIO.LOW)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.HIGH)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.LOW)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.HIGH)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.LOW)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.HIGH)	
sleep(0.2)
GPIO.output(LEDRED, GPIO.LOW)	









