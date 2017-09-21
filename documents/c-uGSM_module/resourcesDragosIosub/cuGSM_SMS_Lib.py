############################################################################################################################################
#cuGSM_SMS_Lib.py v1.01/08September2015 - c-uGSM 1.13 SMS basic functions library 
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
from cuGSM_Serial_Lib import *
from string import replace

noSMS = 0
totSMS = 0
SMSmessage = ["","","",""]

#sendSMS(phno, phtype, message)
#   phno    - phone number - see exambles bellow
#   phtype  - 147/129 - see exambles bellow
#   message - SMS message to be transmited
#   returns 0 on success, 1 on failure
#
#   res = sendSMS(destinationNumber, "129", message)#domestic format numbers
#   res = sendSMS(destinationNumber, "145", message)#international format numbers
#   anyway, check AT command pdf for proper 129/145 parameter/number format usage
def sendSMS(phno, phtype, message):
	res=0
	aGsmWRITE("AT+CMGS=\""+phno+"\","+phtype+"\r")
	res = recUARTdata(">","ERROR",12)
	if(res==0):
		#print("SMS 0 cmd succeed. TEXT next")
		msg = message + chr(0x1A)#adding "send message char" to the message
		res = sendATcommand(msg, ["OK","ERROR"],30)
		#print(msg)
		#if(res==0):
		#	print("SMS 1 cmd succeed.")
	return res

#listSMS()
#   find stored SMS number(==>noSMS) and total SMS number (==>totSMS)
def listSMS():
    global noSMS
    global totSMS
    
    while 1:
        clearInput()
        res = sendATcommand("AT+CPMS?",["OK","+CMS ERROR:"],10)#//+CPMS: "SM",8,50,"SM",8,50,"SM",8,50// +CMS ERROR:
        if(res==0):
            break
        sleep(0.5)
    #print("read from serial:")
    buffd = getResponse()
    #print buffd
    processed = buffd.split(",")
    noSMS = int(processed[1])
    totSMS = int(processed[2])
    #print("noSMS: "+str(noSMS))
    #print("totSMS: "+str(totSMS))

#readSMS(SMSindex)
#   sweet little baby... read the SMS found at SMSindex
#   extract and store the SMS content in global var SMSmessage
#   SMSmessage[0]   type(REC) READ/UNREAD
#   SMSmessage[1]   sender number
#   SMSmessage[2]   SMS date and time
#   SMSmessage[3]   SMS content(message)
def readSMS(SMSindex):
    global sreadlen
    global SMSmessage
    #start read SMS
    aGsmWRITE("AT+CMGR="+str(SMSindex)+",0\r")
    recUARTdata(["OK","ERROR"],5,sreadlen)#receive modem's response...in buffd
    #end read SMS

    buffd = getResponse()
    if(len(buffd)<1):
            return -1

    #print("Modem response:")
    print(buffd)#let's see what modem say
    #print("\r\n")

    #let's interpret and extract the SMS content
    processed = buffd.split(",",4)
    buff = processed[1].split("\"")
    SMSmessage[0]= replace(str(buff[1]),"\"","")#type(REC) READ/UNREAD
    SMSmessage[1]= replace(str(processed[2]),"\"","")#sender number 
    buff = processed[4].split("\"")
    SMSmessage[2]= buff[1]#date and time
    SMSmessage[3]= str(buff[2])[2:-8]#message
    #message has been processed and his content loaded into SMSmessage
    return 0

def getSMSmessage():
    return SMSmessage
def getnoSMS():
    return noSMS
def gettotSMS():
    return totSMS
