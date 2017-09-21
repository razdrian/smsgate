############################################################################################################################################
#c-uGSM-DTMF.py v1.01/08September2015 - c-uGSM 1.13 dial & send DTMF utility demo
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
#HEALTH AND SAFETY WARNING!!!!!!!!!!!!!!!!!!!!
#High power audio (around 700mW RMS)! You can damage your years! Use it with care when headset is connected.
#We recomend to use AT+CLVL=20 (as maximum value), audio setup command in order to limit the output power.

# Raspberry PI - c-uGSM wiring connection
#
# WARNING: WIRING the c-uGSM-gsm board with u-controllers/boards(RPi) must be made with boards UNPOWERED!!
#
# LEGAL DISCLAIMER:
# Incorrect or faulty wiring and/or connection can damage your RPi and/or your c-uGSM board!
# Following directives are provided "AS IS" in the hope that it will be useful, but WITHOUT ANY WARRANTY!
# Do the wiring on your own risk! 
#
# References:
# http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-GPRS-shield-how-to-c-uGSM_kickstart_v_0-92.php
# http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-micro-shield-board-module-RaspberryPI-Arduino-c-uGSM-features-code-examples
# http://itbrainpower.net/images/GSM-SHIELD-RPI-logical-wiring-c-uGSM.png
# http://itbrainpower.net/images/c-uGSM-02-top-marked.jpg
# http://itbrainpower.net/images/c-uGSM-02-bottom-marked.jpg
#
#Connection name    RPi		c-uGSM dial SIM shield (micro)
#ON/OFF	            16		PIN4    - POWER ON/OFF
#RESET 	            18		PIN3    - RESET
#STATUS	            12		PIN10   - STATUS
#
#serial TXD0	    08		PIN2    - TX(RXD)	
#serial RXD0	    10		PIN1    - RX(TXD)
#	
#GND 		    06/14	PIN8	- GND - GROUND 
#
#POWER the c-uGSM shield (micro). IMPORTANT!!!!!!!!!!!!!!!
#Connect as bellow ONLY if you intend to POWER the c-uGSM from RPI 5V and you have LiPol battery connected to RPi 
#Connection name    RPi		c-uGSM dial SIM shield (micro)
#5V 		    02/04	PIN6    - Vin 5V LiPol IN - POWER PIN - input +5V for LiPol charger only  
#
#If you intend to POWER via USB from 5V power supply (Eg.: your phone/tablet Wall Adapter) and you have LiPol battery connected to RPi
#   * plug the uUSB typeA cable end to the c-uGSM USB port. The other USB end of the cable must be plugged to the 5V wall adapter
#   * place a jumper between PIN5[Vusb 5V OUT] and PIN6[Vin 5V LiPol IN] of the c-uGSM shield
#
#If you intend to POWER from INDEPENDENT 5V power supply and you have LiPol battery connected to RPi
#   * c-uGSM PIN6[Vin 5V LiPol IN]   <<==WIRE==>>    External (Switching) Power Supply +5V Output
#   * c-uGSM PIN8[GND]               <<==WIRE==>>    External (Switching) Power Supply GROUND
#
#More POWERING details and POWERING schemas (with or without LiPol configurations):
# http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-GPRS-shield-how-to-c-uGSM_kickstart_v_0-92.php
# 
############################################################################################################################################
# this utility must be runned as root (just use: sudo python yourPythonFileName.py)

destinationNumber=""#usually phone number with International prefix eg. +40 for Romania - in some networks you must use domestic numbers
maxConTime = 30                 #maximum call connected time n seconds
maxDialRetry = 3                #maximum dial retry number

DTMF = "#*01234567890ABCD"      #DTMF string 2 send
terminator ="***"               #logical terminator it is glued at the end of the DTMF string
DTMFdelayTime = 2               # some delay in secs. bw. call connected detection and send the DTMF string 

usePoweringControl = 1  #change it to 0 if you do not want to control powerUP/powerDown the c-uGSM board. In this case, please be sure the c-uGSM board is powered UP(..see c-uGSM_kickstart_v_x-yz.pdf) before run this utility   

#Do not change under following line! Insteed make one copy of the file and play with! 
#Hint: if you make changes of the code, before you run it run clear utility (erase the Python compiled *.pyc files)... 
############################################################################################################################################

import os
import serial
from time import sleep, time
from string import replace

from globalParVar import *
from cuGSM1_13_hw_control import *
from cuGSM_Serial_Lib import *
from cuGSM_Basic_Lib import *
from cuGSM_DTMF_Lib import *

print "Light example - DTMF string send  - dial/redial(for max. "+str(maxDialRetry)+" tries) a destination number, waiting for remote to answer."
print "After the call it is connected, for "+str(DTMFdelayTime)+" secs. before the DTMF string. After a while the connection it is closed."
print "Call disconnection detection remains active."
sleep(1)
print "\r\nHEALTH AND SAFETY WARNING!!!!!!!!!!!!!!!!!!!!HEALTH AND SAFETY WARNING!!!!!!!!!!!!!!!!!!!!"
print "\r\n\r\nHigh power audio module(around 700mW RMS)! You can damage your years! Use it with CARE when HEADSETS are USED."
print "We recomend to use AT+CLVL=20, audio setup command in order to limit the output power."
print "\r\n"
sleep(2)

if not os.getuid() == 0:
    print("please use root privileges! try: \"sudo python yourPythonFileName.py\"")
    exit(0)

if destinationNumber=="":
    print("No destination number has been set!")
    print("Edit the file and set the destinationNumber in line 64\r\n")
    exit(0)

# set SERIAL/USB communication section start
# bellow chose value bw [SER] Serial /dev/ttyAMA0 or [USB] /dev/ttyUSB0
# if module USB port maps to other port as /dev/ttyUSB1, just edit the moduleName_Serial_lib.py...
serialCommunicationVia = SERIALCON      # OVERRIDE the default value loaded from globalParVar.py. here I use via SERIAL communication
setSerialCom(serialCommunicationVia)    # set the current communication option
startSerialCom()                        # open serial communication bw. RPi and c-uGSM shield (micro)
# set SERIAL/USB communication section end
        
# set HARDWARE CONTROL setup & POWER ON section start        
if usePoweringControl==1:
    hwControlSetup()                    # setup the RPi I/O ports

sleep(2)#some delay...

if usePoweringControl==1:
    poweron()

sleep(1)
# set HARDWARE CONTROL setup & POWER ON section end        

# set MODEM STARTUP SETUP section start        
setupMODEM()
print "init audio channel ..."
setAUDIOchannel()
# set MODEM STARTUP SETUP section end        

# MAIN PROGRAM section start        
setupMODEMforDTMFusage()

print "dialing ..."
run = 1
count = 1
#dial/redial/call connected detection loop
res = dial(destinationNumber)
while(run==1):
    res = getcallStatus()
    if(res==0):     #here the other part answer the call...status active
        #sleep(30)   #you can talk 30 seconds
        #hangup()    #hang up the call 
        print("call connected detected...")
        run=0       #call connected event detected => exit loop
    elif(res<0):    #no calls, you may want to redial??
        if (count>=maxDialRetry):
            print("max redialing... giving up...")
            run=0   #max count...exit loop
        else:
            count+=1
            sleep(1.5)
            print("redialing...")
            dial(destinationNumber)
    sleep(0.2)

startTime = time()
run = 1
res = getcallStatus()
if (res==0):                                        #call connected
    while(run==1):
        res = getcallStatus()
        if(res==0):                                 #call connected
            if(int(time() - startTime) == DTMFdelayTime):    #looking for wait
                print ("delay passed. send DTMF string:"+DTMF+" and ending with terminator: "+terminator)
                #usage: sendDTMF(DTMFstring, DTMFterminator, DTMFlenght, DTMFpause)# DTMFlenght and DTMFpause integer msecs. 
                sendDTMF(DTMF, terminator, 100, 100) #just send the DTMF
                sleep(4)
                hangup()                            #close the call
                run = 0                             #exit the loop
            elif(time() - startTime > maxConTime):    #looking for maxConTime sec maximum connection time
                print("max time... hang up...")
                hangup()
                run=0
            sleep(0.25)                              #wait a little
        else:
            print("call is no more active...")
            run=0                                   #exit loop

sleep(1)

disableDTMFdetection()
#print("\r\nusage: sendDTMF(DTMFstring, DTMFterminator, DTMFlenght, DTMFpause)# DTMFlenght and DTMFpause integer msecs.\r\n")
#sleep(3)
# MAIN PROGRAM section end        


# stop SERIAL COMMUNICATION section start        
stopSerialCom()                             # close modem communication
# stop SERIAL COMMUNICATION section end        

# HARDWARE CONTROL release & POWER OFF section start        
if usePoweringControl==1:
    poweroff()                              #shutdown modem

if usePoweringControl==1:
    hwControlRelease()                      # free GPIO
# HARDWARE CONTROL release & POWER OFF section end        


print("\r\n\r\nThat's all folks!\r\n")
