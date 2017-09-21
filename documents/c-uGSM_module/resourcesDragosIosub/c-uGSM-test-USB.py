############################################################################################################################################
#c-uGSM-test-USB.py v1.01/08September2015 - c-uGSM 1.13 test USB communication utility
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

usePoweringControl = 1#change it to 0 if you do not want to control powerUP/powerDown the c-uGSM board. In this case, please be sure the c-uGSM board is powered UP(..see c-uGSM_kickstart_v_x-yz.pdf) before run this utility   

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

# bellow chose value bw [SER] Serial /dev/ttyAMA0 or [USB] /dev/ttyUSB0
# if module USB port maps to other port as /dev/ttyUSB1, just edit the moduleName_Serial_lib.py...
serialCommunicationVia = USBCON         # in this example we use the comunication via USB port

if(serialCommunicationVia!=USBCON):
    print "Light example - just testing SERIAL communication (/dev/ttyAMA0)."
else:
    print "Light example - just testing USB communication (/dev/ttyUSB0)."
sleep(1)


print "\r\nHEALTH AND SAFETY WARNING!!!!!!!!!!!!!!!!!!!!HEALTH AND SAFETY WARNING!!!!!!!!!!!!!!!!!!!!"
print "\r\n\r\nHigh power audio module(around 700mW RMS)! You can damage your years! Use it with CARE when HEADSETS are USED."
print "We recomend to use AT+CLVL=20, audio setup command in order to limit the output power."
print "\r\n"
sleep(2)

if not os.getuid() == 0:
    print("please use root privileges! try: \"sudo python yourPythonFileName.py\"")
    exit(0)

# set SERIAL/USB communication section start
setSerialCom(serialCommunicationVia)    # OVERRIDE the default value loaded from globalParVar.py
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
# set MODEM STARTUP SETUP section end        

# MAIN PROGRAM section start        
print("Read IMEI (modem id)")
IMEI=getIMEI()
print(IMEI)
print ""

print("Read IMSI (SIM id)")
IMSI = getIMSI()
print IMSI

print("checking 4 gsm registration")
res = wait4GSMReg(5)
if(res==1):
    print("ready...")

print("Let's check the signal level")
res = getSignalStatus()
print "Signal: "+ str(res)
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

if(serialCommunicationVia!=USBCON):
    print("\r\n\r\nThat's all folks!\r\nMaybe u want to try communication over USB...")
    print("Read config how to in c-uGSM-test-USB.py. Configure the hardware and after that run c-uGSM-test-USB.py\r\n")
else:
    print("\r\n\r\nThat's all folks!\r\nMaybe u want to try communication over SERIAL...")
    print("Read config how to in c-uGSM-test-SERIAL.py. Configure the hardware and after that run c-uGSM-test-SERIAL.py\r\n")
