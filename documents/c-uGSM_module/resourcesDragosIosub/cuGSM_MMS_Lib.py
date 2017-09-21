############################################################################################################################################
#cuGSM_MMS_Lib.py v1.01/08April2016 - c-uGSM 1.13 MMS send library 
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

#your MMS mobile provider related settings
MMSAPN              = "mms"
MMSCURL             = "http://wap.mms.orange.ro:8002"
MMSCPROXYADDRESS    = "62.217.247.252"
MMSCPROXYPORT       = "8799"

###############################################################################################################
#DO NOT CHANGE BELLOW THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
###############################################################################################################
#from globalParVar import *
from time import sleep
#from cuGSM_Basic_Lib import wait4GPRSReg
#from string import replace
from cuGSM_Serial_Lib import *

#clear all MMS content
def clearMMS():
    sendATcommand("AT+QMMSW=0",["OK","ERROR"],3)
		
#shut down MMS IP
def deactMMSPDP():
    sendATcommand("AT+QIDEACT",["OK","ERROR"],10)

# loadMMSMode() prepare modem for MMS send
# call this "setup" before you performe any MMS task
def loadMMSMode():
    clearMMS()
    deactMMSPDP()
    sendATcommand("AT+QIFGCNT=0",["OK","ERROR"],3)
    sleep(0.1)
    #set MMS APN
    sendATcommand("AT+QICSGP=1,\""+MMSAPN+"\"",["OK","ERROR"],3)
    #set MMSC URL (PROXY & POST)
    sendATcommand("AT+QMMURL=\""+MMSCURL+"\"",["OK","ERROR"],3)
    #set MMSC PROXY ADDRESS & PORT
    sendATcommand("AT+QMMPROXY=1,\""+MMSCPROXYADDRESS+"\","+MMSCPROXYPORT,["OK","ERROR"],3)


#you can add multiple receipments address (phone numbers and emails). Simply call this function for each address.
def addReceipment(receipment):
    sendATcommand("AT+QMMSW=1,1,\""+receipment+"\"",["OK","ERROR"],3)

#set the MMS subject
def setMMSSubject(messageSubject):
    res = 0
    sendATcommand("AT+QMMSCS=\"ASCII\",1",["OK","ERROR"],3)
    aGsmWRITE("AT+QMMSW=4,1\r")
    res = recUARTdata(">","ERROR",3)
    if(res==0):
        #print("0 cmd succeed. TEXT next")
        #adding "END/RDY message char" to the message
        res = sendATcommand(messageSubject + chr(0x1A), ["OK","ERROR"],3)
    return res

	
#RAM disk file support for MMS attachments
def delAttachement(filename):
    sendATcommand("AT+QFDEL=\"RAM:"+filename+"\"",["OK","ERROR"],3)
	
#RAM disk file support for MMS attachments
def uplAttachement(filename, filecontent):
    res = 0
    res = sendATcommand("AT+QFUPL=\"RAM:"+filename+"\","+str(len(filecontent))+"\r",["CONNECT","ERROR"],3)
    #aGsmWRITE("AT+QMMSW=4,1\r")
    #res = recUARTdata(">","ERROR",3)
    if(res==0):
        aGsmWRITE(filecontent)
        res = recUARTdata("OK","ERROR",3)
    return res

#you can add multiple attachements, previously uploaded to the RAM disk
def addAttachement(filename):
    return sendATcommand("AT+QMMSW=5,1,\"RAM:"+filename+"\"",["OK","ERROR"],3)

#here it is
def sendMMS():
    res = 0
    res = sendATcommand("AT+QMMSEND=1",["0,0","ERR"],30)
    deactMMSPDP()
    return res
