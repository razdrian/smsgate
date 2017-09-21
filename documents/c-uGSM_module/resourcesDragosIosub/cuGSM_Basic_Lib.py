############################################################################################################################################
#cuGSM_Basic_Lib.py v1.01/08September2015 - c-uGSM 1.13 BASIC FUNCTIONS library 
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
from time import sleep, time
from globalParVar import *
from cuGSM_Serial_Lib import *

activeSIM = 0 #store the active SIM id; 0(zero)- TOP SIM, or 1(one)- BOTTOM SIM

def setupMODEM():
    sendATcommand("AT+QIMODE=0",["OK","ERROR"],5)
    sendATcommand("AT+QINDI=0",["OK","ERROR"],5)
    sendATcommand("AT+QIMUX=0",["OK","ERROR"],5)
    sendATcommand("AT+QIDNSIP=0",["OK","ERROR"],5)
    print ("SIM ready? no PIN checking?")
    while 1:
        clearInput()
        sendATcommand("AT+CPIN?",["OK","ERROR"],5)
        buffd = getResponse()
        if(buffd.find("READY")):
            print ("ready...")
            break
        print "SIM is not ready. Please remove the PIN verification!"
    sleep(1)
    print ("SIM ready 4 SMS processing?")
    while 1:
        clearInput()
        res = sendATcommand("AT+CPBS?",["OK","ERROR"],5)
        buffd = getResponse()
        if(buffd.find("+CME ERROR") < 0):
            break
        sleep(1)
        print("not yet...")

    res = sendATcommand("AT+CPBS=\"SM\"",["OK","ERROR"],7)
#    if(res==0): 
#	    print("SIM storage has been selected\r\n");

    res = sendATcommand("AT+CMGF=1",["OK","ERROR"],5)
    if(res==0):
        print("Set SMS mode TEXT succeed")
    #AT+CNMI=2,1,0,0,0//standard mode
    #AT+CNMI=2,0,0,0,0
    res = sendATcommand("AT+CNMI=2,0,0,0,0\r",["OK","ERROR"],5)
#    if(res==0):
#        print("Disable TE SMS notification succeed")
    clearInput()
    print("ready to go...")

#utility that read and return the IMEI (MODEM related identifier)
def getIMEI():
    sendATcommand("AT+GSN",["OK","ERROR"],3)
    buffd = getResponse()
    IMEI = buffd[9:-8]
    #print(IMEI)
    return IMEI

#utility that read and return the IMSI (SIM related identifier) 
def getIMSI():
    clearInput()
    res = sendATcommand("AT+CIMI",["OK","ERROR"],3)
    buffd = getResponse()
    if(res==0 and len(buffd) > 18):
        return buffd[buffd.find("AT+CIMI")+10:buffd.find("OK")-4]
    else:
        return ''

#read GSM registration status
def wait4GSMReg(to): #to -timeout in seconds
    res=1
    ret=-2
    startTime = time()
    print("query GSM registration status")
    while(time()-startTime < to):
        res = sendATcommand("AT+CREG?",["OK","ERROR"],10)
        if(res==0):
            buffd = getResponse()
            if(buffd.find("0,1") > 0 or buffd.find("0,5") > 0):#second for Roaming registration*
               offsetTime=0
               #state=state+1
               print("Ready")
               ret=1
               return ret#modem registered, return 1
            else:
               print("Not yet")
        sleep(0.5)
        return ret#timeout+not registered ..return -2

#read GPRS registration status
def wait4GPRSReg(to): #to -timeout in seconds
    ret=-2
    startTime = time()
    print("query GPRS registration status")
    while(time()-startTime < to):
        res = sendATcommand("AT+CGREG?",["OK","ERROR"],10)
        if(res==0):
            buffd = getResponse()
            if(buffd.find("0,1") > 0 or buffd.find("0,5") > 0):#second for Roaming registration*
               offsetTime=0
               #state=state+1
               print("Ready")
               ret=1
               return ret#modem registered, return 1
            else:
               print("Not yet")
        sleep(0.5)
        return ret#timeout+not registered ..return -2

#read GSM signal status
def getSignalStatus():
    h=0
    res = sendATcommand("AT+CSQ",["OK","ERROR"],10)
    if(res==0):
        buffd = getResponse()
        #print buffd
        startat = buffd.find(": ")
        endat = buffd.find(",")
        #print buffd[startat+2:endat]
        res = int(buffd[startat+2:endat])
        #print str(res)
        if(res==99):
            h=0
        elif(res>-1 and res<8):#-113dBm -> -99dBm
            h=1
        elif(res>7 and res<13):#-99dBm -> -89dBm
            h=2
        elif(res>12 and res<18):#-89dBm -> -79dBm
            h=3
        elif(res>17 and res<23):#-79dBm -> -69dBm
            h=4
        elif(res>22 and res<28):#-69dBm -> -59dBm
            h=5
        elif(res>27 and res<31):#-59dBm -> -53dBm
            h=6
        elif(res>=31):#>-53dBm
            h=7
        #print signal as some graph
        sglLevel = ("Signal level  ")
        j=0
        while(j<h):
            sglLevel += ("#")
            j+=1
        print sglLevel
    else:
        print("SIGERR")
    return h


#setAUDIOchannel()
#   Prepare c-uGSM for audio part usage
#   High power audio (around 700mW RMS)! You can damage your years! Use it with care when headset is connected.
#   We recomend to use AT+CLVL=20, audio setup command in order to limit the output power.
def setAUDIOchannel():
  sendATcommand("AT+QAUDCH=2", ["OK","ERROR"],2)#use audio channel(2-standard for c-uGSM)
  sendATcommand("AT+QMIC=2,14", ["OK","ERROR"],2)#set mic channel(2), mic gain
  sendATcommand("AT+CLVL=20", ["OK","ERROR"],2)#set output POWER! Do NOT exceed value of 25 if headset is used!

#activateTopSIM()
#   call this function if you want to test/use SIM inserted in the SIM SOCKET placed on BOTTOM of the c-uGSM dual SIM socket
def activatePrimarySIM():
    setActiveSIM(0)

#activateBottomSIM()
#   call this function if you want to test/use SIM inserted in the SIM SOCKET placed SIM SOCKET placed on TOP of the c-uGSM dual SIM socket
def activateSecondarySIM():
    setActiveSIM(1)

#dial(number)
#   just dial "number"
#   use it in conjunction with getcallStatus() to see if remote ANSWER/BUSY....
def dial(number):
    return sendATcommand("ATD"+str(number)+";",["OK","ERROR"],3)

#hangup()
#   hangup the call
def hangup():
    return sendATcommand("ATH",["OK","ERROR"],3)

#answer()
#   answer the call
def answer():
    return sendATcommand("ATA",["OK","ERROR"],3)

#enableAutoAnswer()
#   set auto answer at ringCnt RING 
def enableAutoAnswer(ringCnt):
    return sendATcommand("ATS0="+str(ringCnt),["OK","ERROR"],3)

#disableAutoAnswer()
#   disable auto answer 
def disableAutoAnswer():
    return sendATcommand("ATS0=0",["OK","ERROR"],3)


#setActiveSIM(SIM)
#   Set the active SIM, Active SIM value will be stored in activeSIM var
def setActiveSIM(SIM):
    if(SIM < 0 or SIM >1):#SIM can be 0(zero)- TOP SIM, or 1(one)- BOTTOM SIM
        return
    res = sendATcommand("AT+CFUN=0", ["OK","ERROR"],10)#shutdown GSM part of the modem
    sleep(1)#just delay a while
    print("set active SIM to: "+str(SIM))
    res = sendATcommand("AT+QDSIM="+str(SIM), ["OK","ERROR"],10)#execute change SIM cmd 
    sleep(1)#just delay a while
    res = sendATcommand("AT+CFUN=1", ["OK","ERROR"],10)#wakeup GSM part of the modem 
    activeSIM = SIM#load active SIM value
    sleep(5)#just delay a while

#setActiveSIM(SIM)
#return the active SIM value
def getActiveSIM(SIM):
    return activeSIM

#int getcallStatus()
#   detects if the voice call is CONNECTED
#   returns: 
#       0 Active   CONNECTED   BOTH
#       1 Held                 BOTH
#       2 Dialing (MO call)    OUTBOUND
#       3 Alerting (MO call)   OUTBOUD
#       4 Incoming (MT call)   INBOUD
#       5 Waiting (MT call)    INBOUD
def getcallStatus():
    print("get connection status...")
    res = sendATcommand("AT+CLCC", ["OK","ERROR"],2)#CHECK CONNECTION STATUS ...RETURN +CLCC: 1,0,0,0,0,"dialed/dialer NO", 129 ISDN/145 INTERNATIONAL format
    buffd = getResponse()
    if(res==0):
        pch0 = buffd.find("+CLCC: ")
        if(pch0 > 0):
            #pch1 = buffd.find("OK")
            #strncpy(content, pch0+7, 5)
            content = buffd[pch0+7:pch0+12]
            #print(content)
            #print (content[4])
            dstat=int(content[4])
            if(dstat==0):
                print("CONNECTED")
            elif(dstat==2):
                print("DIALING")
            elif(dstat==3):
                print("RING-OUTBOUND")
            elif(dstat==4):
                print("RING-INBOUND")
            return dstat
        else:#connection ended (BUSY or NO CARRIER)
            print("NO CONNECTION")
            return -1
    print("CMD ERROR")
    return -2;


