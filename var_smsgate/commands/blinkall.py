#!/usr/bin/python

LEDYELLOW=37
LEDRED=40
import sys
import RPi.GPIO as GPIO
from time import *

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LEDRED, GPIO.OUT)
GPIO.setup(LEDYELLOW, GPIO.OUT)



GPIO.output(LEDRED, GPIO.HIGH)
GPIO.output(LEDYELLOW, GPIO.LOW)
sleep(0.3)
GPIO.output(LEDRED, GPIO.LOW)
GPIO.output(LEDYELLOW, GPIO.HIGH)
sleep(0.3)
GPIO.output(LEDRED, GPIO.HIGH)
GPIO.output(LEDYELLOW, GPIO.LOW)
sleep(0.3)
GPIO.output(LEDRED, GPIO.LOW)
GPIO.output(LEDYELLOW, GPIO.HIGH)
sleep(0.3)
GPIO.output(LEDRED, GPIO.HIGH)
GPIO.output(LEDYELLOW, GPIO.LOW)
sleep(0.3)
GPIO.output(LEDRED, GPIO.LOW)
GPIO.output(LEDYELLOW, GPIO.HIGH)
sleep(0.3)
GPIO.output(LEDRED, GPIO.HIGH)	
GPIO.output(LEDYELLOW, GPIO.LOW)
sleep(0.3)
GPIO.output(LEDRED, GPIO.LOW)
GPIO.output(LEDYELLOW, GPIO.LOW)






