#definitions for c-uGSM control lines on RPi GPIO mode 
POWER = 11
RESET = 13
STATUS = 7

#############################################################################################################################
USBCON = 1                      # do not change this
SERIALCON = 0                   # do not change this
#############################################################################################################################

#select bw. USB or SERIAL communication, bellow
serialCommunicationVia = USBCON         # COMMUNICATION VIA USB
#serialCommunicationVia = SERIALCON      # COMMUNICATION VIA SERIAL

#communication speed. we recommend usage of 19200 bps speed. 
serialSpeed = 19200 


#definitions of some program global variables
i=0
buffd =""
fileBuffer = ""

#############################################################################################################################
#DO NOT CHANGE DEFINITIONS BELLOW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#############################################################################################################################

sreadlen = 100                  #max chars to read in one try over serial

GET = 0				#GET METHOD 
POST = 1			#POST METHOD
SSLENABLED = 1                  #use SSL ENABLED (HTTPS)
SSLDISABLED = 0                 #don't use SSL (HTTP)

IPINITIAL = 0			#TCPIP IDLE 
IPSTART = 1			#TCPIP REGISTERED
IPCONFIG = 2			#startup to activate GRS/CSD context
IPGPRSACT = 4			#GRS/CSD context ACTIVATED
IPSTATUS = 5			#local IP address obtained
IPCONNECTING = 6		#SOCKET CONNECTING ==>"TCP CONNECTING" or "UDP CONNECTING"
IPCLOSE = 7			#SOCKET CLOSED
CONNECTOK = 8			#SOCKET CONNECTED
PDPDEACT = 9			#GRS/CSD context DE-ACTIVATED (unknown reason)
