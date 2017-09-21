#!/usr/bin/python

LEDYELLOW=37
import sys
import RPi.GPIO as GPIO
from time import *

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LEDYELLOW, GPIO.OUT)


GPIO.output(LEDYELLOW, GPIO.HIGH)
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.LOW)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.HIGH)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.LOW)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.HIGH)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.LOW)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.HIGH)	
sleep(0.6)
GPIO.output(LEDYELLOW, GPIO.LOW)	






