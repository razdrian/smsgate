############################################################################################################################################
#cuGSM1_13_hw_control.py v1.01/08September2015 - c-uGSM 1.13 rev 1 HARDWARE CONTROL library 
#COPYRIGHT (c) 2015 Dragos Iosub / R&D Software Solutions srl
#
#You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH c-uGSM DEVICES USAGE. Modifications, derivates and redistribution 
#of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms 
#of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.
#
#This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
#warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#Dragos Iosub, Bucharest 2015.
#http://itbrainpower.net
############################################################################################################################################
import os
import RPi.GPIO as GPIO
from globalParVar import *
from time import sleep
from cuGSM_Serial_Lib import *

# getModemState()
# returns 1 if the modem is up, 0 else
def getModemState():
        return GPIO.input(STATUS)

# getModemStateByAT()
# returns 1 if the modem is running, 0 else
# can be used as substitute for getModemState()
def getModemStateByAT():
        aGsmWRITE("+++\r\n")
        aGsmWRITE(chr(0x1B)+"\r\n")
        aGsmWRITE("AT\r\n")
        aGsmWRITE("ATE1\r\n")
        aGsmWRITE("ATV1\r\n")
        clearSInput()
        clearInput()
        res = sendATcommand("AT",["OK","ERROR"],1)
        if(res>0):
                return 1
        else:
                return 0

def poweron():
	#if not GPIO.input(STATUS):
	if not(getModemState()):
		print ("try to wake c-uGSM")
		#GPIO.output(POWER,GPIO.HIGH)
		#sleep(1)
		#GPIO.output(POWER,GPIO.LOW)
		GPIO.output(POWER,GPIO.LOW)
		sleep(1)
		GPIO.output(POWER,GPIO.HIGH)
	sleep(5)	
	#if GPIO.input(STATUS):
	if (getModemState()):
		print("c-uGSM is up")
	else:
		print("failure powering c-uGSM")
		exit(100)
	
def poweroff():
	#if GPIO.input(STATUS):
	if (getModemState()):
		print ("try to shutdown c-uGSM")
		#GPIO.output(POWER,GPIO.HIGH)
		#sleep(1)
		#GPIO.output(POWER,GPIO.LOW)
		GPIO.output(POWER,GPIO.LOW)
		sleep(1)
		GPIO.output(POWER,GPIO.HIGH)
	sleep(8)
	#if not GPIO.input(STATUS):
	if not(getModemState()):
		print("c-uGSM is down")
	else:
		print("failure powering off c-uGSM")
		exit(100)

def restartModem():
    poweroff()
    sleep(3)
    poweron()

def resetModem():
	print ("try to reset c-uGSM")
	#GPIO.output(RESET,GPIO.HIGH)
	#sleep(1)
	#GPIO.output(RESET,GPIO.LOW)
	GPIO.output(RESET,GPIO.LOW)
	sleep(1)
	GPIO.output(RESET,GPIO.HIGH)
	sleep(8)
	#if not GPIO.input(STATUS):
	if not(getModemState()):
		print("c-uGSM is down")
	else:
		print("failure reset c-uGSM")
		exit(100)

def hwControlSetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.setup(STATUS, GPIO.IN)
        #GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        #GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)
    except:
        GPIO.cleanup()#free GPIO
        GPIO.setup(STATUS, GPIO.IN)
        #GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        #GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setwarnings(True)
    
def hwControlRelease():
    GPIO.cleanup()#free GPIO
