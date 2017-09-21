############################################################################################################################################
#cuGSM_Serial_Lib.py v1.011/15April2016 - c-uGSM 1.13 Serial library 
#COPYRIGHT (c) 2016 Dragos Iosub / R&D Software Solutions srl
#
#You are legaly entitled to use this SOFTWARE ONLY IN CONJUNCTION WITH c-uGSM DEVICES USAGE. Modifications, derivates and redistribution 
#of this software must include unmodified this COPYRIGHT NOTICE. You can redistribute this SOFTWARE and/or modify it under the terms 
#of this COPYRIGHT NOTICE. Any other usage may be permited only after written notice of Dragos Iosub / R&D Software Solutions srl.
#
#This SOFTWARE is distributed is provide "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
#warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#Dragos Iosub, Bucharest 2016.
#http://itbrainpower.net
############################################################################################################################################
from globalParVar import *
from time import time,sleep
import serial

def setSerialCom( myport):
    global serialCommunicationVia
    serialCommunicationVia = myport

def stopSerialCom():
    global agsm
    try:
        agsm.close()
        print("Close SERIAL")
    except:
        dummy=0
        print("ERROR closing SERIAL")

def startSerialCom():
    global agsm
    global serialCommunicationVia

    sleep(1)
    print("Open connection")
    try:
        if(serialCommunicationVia == SERIALCON):
            agsm = serial.Serial("/dev/ttyAMA0", serialSpeed, timeout=1)
            print("using SERIAL interfacing")
        else:
            agsm = serial.Serial("/dev/ttyUSB0", serialSpeed, timeout=1)
            print("using USB interfacing")
    except:
        print("ERROR opening connection")
        stopSerialCom()
        agsm.open()
        print("Try again...")

#    if(serialCommunicationVia == SERIALCON):
#        agsm = serial.Serial("/dev/ttyAMA0", serialSpeed, timeout=1)
#        print("using SERIAL interfacing")
#    else:
#        agsm = serial.Serial("/dev/ttyUSB0", serialSpeed, timeout=1)
#        print("using USB interfacing")
#    try:
#        agsm.open()
#        print("Open SERIAL")
#    except:
#        print("ERROR opening SERIAL")
#        stopCom()
#        agsm.open()
    aGsmWRITE("+++\r\n")
    aGsmWRITE(chr(0x1B)+"\r\n")
    aGsmWRITE("AT\r\n")
    aGsmWRITE("ATE1\r\n")
    aGsmWRITE("ATV1\r\n")
    clearSInput()
    clearInput()

#recUARTdata(endchars,to,tm)
#   read from modem - read string is loaded in global var buffd
#   looking for endchars [SUCCESS STRING,FAILURE STRING] and to - TIMEOUT
#   return 0 for SUCCESS, 1 for FAILURE, -1 for timeout
#   tm how many chars to read(maximum) in one loop from serial
def recUARTdata(endchars,to,tm):
	global buffd
	global agsm
	buffd = ''
	dt = ''
	t = time()
	while 1:
		if time()-t > to:
			break
		#avbytes = agsm.inWaiting()
		dt = agsm.read(tm)
		buffd = buffd + dt
		if(len(buffd) > 0):
			j = 0
			for x in endchars:
				if (buffd.find(x) != -1):
					agsm.flushInput()
					return j
				j=j+1
	agsm.flushInput()
	print ("CDTO![" + buffd + "]\r\n")
	return -1

#sendATcommand(command, endchars,to)
#   command +"\r\n" is forwarded to modem
#   looking for endchars [SUCCESS STRING,FAILURE STRING] and to - TIMEOUT
#   return 0 for SUCCESS, 1 for FAILURE, -1 for timeout
#   modem response is loaded in global var buffd
def sendATcommand(command, endchars,to):
    global agsm
    global sreadlen
    agsm.write(command+"\r\n")
    return (recUARTdata(endchars,to,sreadlen))

#getResponse()
#   just return the buffd (call if you need to read the modem response...after sendATcommand, ...)
def getResponse():
    return buffd
        
#aGsmWRITE(command)
#   just write command to serial without CR LF
def aGsmWRITE(command):
    global agsm
    agsm.write(command)

def clearInput():
    agsm.flushInput()

def clearSInput():
    if(agsm.inWaiting()):
        agsm.read(4096)

def readline(timeout):#timeout in miliseconds
    global buffd
    cnt=0
    c = ""
    res=0
    buffd = ""
    startTime = 1000*time()
    while(1):
        #c=agsmSerial.read();
        c = agsm.read(1)
        res = 1 #return found
        #if(c == '\n') break;
        if(len(c) > 0):
            if(ord(c) == 0x0A):
                break
            buffd = buffd + c
        if(timeout > 0 and 1000*time() - startTime > timeout):
            res = -1 #return timeout
            break
    return res

