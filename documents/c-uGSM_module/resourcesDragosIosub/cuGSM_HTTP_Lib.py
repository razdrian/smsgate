############################################################################################################################################
#cuGSM_HTTP_Lib.py v1.01/08September2015 - c-uGSM 1.13 PPP/IP/HTTP library 
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

#your SIM's GPRS related settings, next
GPRS_context="INTERNET"
GPRS_user="INTERNET"
GPRS_password=""

#your IP related settings, next
SERVER_ADDRESS="itbrainpower.net"		#server URL - used also for http URL...
SERVER_PROTOCOL="TCP"        			#server PROTOCOL TCP or UDP (for HTTP is TCP)

#your HTTP related settings, next
HTTP_PATH="/a-gsm/test/echo"         	        #your WEB application path... 
###############################################################################################################
#DO NOT CHANGE BELLOW THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
###############################################################################################################
from globalParVar import *
from time import sleep
from cuGSM_Basic_Lib import wait4GPRSReg
from string import replace
from cuGSM_Serial_Lib import *


#here start...some vars initialisation 
HTTP_PROTOCOL="http://"				#server protocol+ can be HTTP or HTTPS
SERVER_PORT="80"        			#server PORT (usual for HTTP is 80 and for HTTPS is 443)
IP_STATE = 0

def setSSLMODE(SSLMODE):
    global HTTP_PROTOCOL
    global SERVER_PORT
    if(SSLMODE==1):
        HTTP_PROTOCOL="https://"
        SERVER_PORT="443"
    else:
        HTTP_PROTOCOL="http://"
        SERVER_PORT="80"
		

# loadIPMode() prepare modem for IP usage
# call this "setup" before you performe any PPP/IP related AT command
def loadIPMode():
    sendATcommand("AT+QIMODE=0",["OK","ERROR"],2)
    sendATcommand("AT+QINDI=0",["OK","ERROR"],2)
    sendATcommand("AT+QIMUX=0",["OK","ERROR"],2)
    sendATcommand("AT+QIDNSIP=1",["OK","ERROR"],2)

# getIPState()
#	check send data ACK...
#	IP_STATE  <== 1-9 - IP/socket transmission status
#	1	- modem ok
#	<0	- modem freezed...resetModem() + restartMODEM()
def getIPState():
    global IP_STATE
    aGsmWRITE("ATE0\r\n")
    sleep(0.1)
    aGsmWRITE("ATV0\r\n")
    sleep(0.2)
    clearSInput()
    aGsmWRITE("AT+QISTAT\r\n")
    if(readline(500) < 1):
        aGsmWRITE("ATE1\r\n")
        aGsmWRITE("ATV1\r\n")
        return -1
    buffd = getResponse()
    #print(buffd)
    ch = buffd[2]
    IP_STATE = ord(ch)-0x30
    aGsmWRITE("ATE1\r\n")
    aGsmWRITE("ATV1\r\n")
    sleep(0.2)
    clearSInput()
    #print("retrived state >> "+str(IP_STATE))
    sleep(0.2)
    return 1 


def openContext():
    global IP_STATE
    global GPRS_context
    global GPRS_user
    global GPRS_password
    #prepareIPMode()
    print("try to set the GPRS context")
    res = sendATcommand("AT+QIREGAPP=\""+GPRS_context+"\",\""+GPRS_user+"\",\""+GPRS_password+"\"",["OK","ERROR"],10)
    #buffd=getResponse()
    #print("debug>> "+ buffd)
    if (res==0):
        #tm=time()
        print("success...")
    #elif(time()-tm > 10):
    #    if usePoweringControl==1:
    #        restartModem()
    else:
        return -100

    print("try to activate GPRS context")
    res = sendATcommand("AT+QIACT",["OK","ERROR"],30)
    #buffd=getResponse()
    #print("debug>> "+ buffd)
    if (res!=0):
        print("fail..")
        return -200
    else:
        print("success...")

    print("GET local IP")
    clearSInput()
    aGsmWRITE("AT+QILOCIP\r\n")
    sleep(0.01)
    readline(10)            #remove command modem echo
    res = recUARTdata(["\r\n","ERR"],10,100)
    buffd = getResponse()
    print(buffd)            # show local IP address
    if(res == 0):
        print("success...")
    else:
        print("error...dhcp process failed/timeout")
        return -300

    getIPState() #update IP_STATE
    return 0

def closeContext():
    print("GPRS context de-activate")
    sendATcommand("AT+QIDEACT",["OK","ERROR"],30)
    getIPState() #update the global IP_STATE
    
# sendHTTPData(HTTP_VARIABLES, METHOD, SSL)
# returns:
#       0 success
#       1 some error reading returned data
#       2 can not send data
#       3 DNS error
#       10 PDP unavailable before send data
#       -100 error on setting the GPRS context 
#       -200 error on activating the PDP / GPRS context 
#       -300 error on obtaining local IP address
#       -500 GPRS NOT REGISTERED
def sendHTTPData(HTTP_VARIABLES, METHOD, SSL):
    global buffd 
    global HTTP_PROTOCOL
    global SERVER_PORT
    global SERVER_ADDRESS 
    global HTTP_PATH 
    global buffd
    global IP_STATE

    tChars=""
    totalChars = 0

    HTTP_VARIABLES = replace(HTTP_VARIABLES," ", "%20") # replace SPACES with correspondent HTML CHAR CODE

    setSSLMODE(SSL)     #set SSL encription or not

    if (wait4GPRSReg(5)!=1):
        print "GPRS NOT REGISTERED!!!"
        return -500
    getIPState() #update IP_STATE
    print("IPSTATE: "+str(IP_STATE))

    if (not(IP_STATE == 5 or IP_STATE == 7)):
        closeContext()
        res=openContext()   #also update IP_STATE before return
        if(res!=0):
            return res #errors or timeout(modem freezed) -100, -200, -300
    print("IPSTATE: "+ str(IP_STATE))
    if(IP_STATE == 5 or IP_STATE == 7):#the PDP ready
        #prepare POST/GET request
        totalChars = 0 

        totalChars = len(HTTP_PROTOCOL) 
        totalChars += len(SERVER_ADDRESS)  
        totalChars += len(":")  
        totalChars += len(SERVER_PORT)  
        totalChars += len(HTTP_PATH)
        if(METHOD == GET):
            totalChars += 1#"?"
            totalChars += len(HTTP_VARIABLES)

        tChars = str(totalChars)

        print("send data...")
        #print(HTTP_PROTOCOL+SERVER_ADDRESS+HTTP_PATH)
        print(HTTP_PROTOCOL+SERVER_ADDRESS+":"+SERVER_PORT+HTTP_PATH)

        clearSInput()      

        aGsmWRITE("AT+QHTTPURL=")
        aGsmWRITE(tChars)
        aGsmWRITE(",10")      
        aGsmWRITE("\r\n")      
        sleep(0.500)      
        readline(5000) #search for CONNECT     

        aGsmWRITE(HTTP_PROTOCOL) 
        aGsmWRITE(SERVER_ADDRESS) 
        aGsmWRITE(":")  
        aGsmWRITE(SERVER_PORT)  
        aGsmWRITE(HTTP_PATH)
        if(METHOD == GET):
            aGsmWRITE("?")
            aGsmWRITE(HTTP_VARIABLES)

        aGsmWRITE("\r\n")
        
        clearSInput()

        if(METHOD == GET):#GET method
            res = sendATcommand("AT+QHTTPGET=50",["OK","ERROR"],20)#wait for ok ---send http get--  20sec
            #res = fATcmd(F("+QHTTPGET=50"),20); //wait for ok ---send http get--  20sec

        else:#POST method                
            totalChars = len(HTTP_VARIABLES)
            #memset(tChars, 0x00, sizeof(tChars));
            #sprintf(tChars,"%i",totalChars);
            tChars=str(totalChars)

            aGsmWRITE("AT+QHTTPPOST=")
            aGsmWRITE(tChars)#total chars
            aGsmWRITE(",30,50")
            aGsmWRITE("\r\n")

            res = recUARTdata(["CONNECT","ERROR"],20,100)  

        if(res==0):
            if(METHOD != GET):#POST method ==> here efective write data
                #send post data
                sleep(0.250)
                clearSInput()
                aGsmWRITE(HTTP_VARIABLES)
                aGsmWRITE("\r\n")      
                res = recUARTdata(["OK","ERROR"],20,100)
            else:
                res = 0
            if(res==0):#//real data has been POSTed    
                res = sendATcommand("AT+QHTTPREAD=30",["OK","ERROR"],32)
                buffd = getResponse()
                #res = fATcmd(F("+QHTTPREAD=30"),32);        
                if(res==0):
                    #print("server return data:\r\n")
                    #print(buffd)
                    #extract RESPONSE start
                    pch1 = buffd.find("OK\r\n")
                    pch0 = buffd.find("CONNECT")
                    pch0 = pch0 + 7 + 2
                    buffd = buffd[pch0: pch1 - 2]
                    #extract RESPONSE stop  
                    #print("processed data:")
                    #print('"'+buffd+'"')
                    return 0
                else:
                    print("some error reading data...")        
                    #print(buffd)
                    return 1
            else:#real data post return ERROR or TIMEOUT
                #check for 3813....DNS error
                #check for 3825....TIMEOUT DATA..la POST
                #check for 3822....la GET
                print("can not POST data!")
                return 2#show error
        else:
            print("DNS error?!")
            return 3#show error
        
    else:#NO PDP!
        print("no sheet! PDP unavailable before send data ")
        return 10#show error

def getHTTPResponse():
    return buffd


# socketOpen    NOT NEEDED for HTTP client data handling (upload/download)!!!!
# return:
#	0 	connected
#	1 	connect fail
#	-1	timeout
def socketOpen():#todo ==> update initial server port value
    global HTTP_PROTOCOL
    global SERVER_PORT
    global SERVER_ADDRESS 
    res=0
    print("Socket open >>> ")
    #res = sendATcommand("AT+QIOPEN=\""+SERVER_PROTOCOL+"\",\""+SERVER_ADDRESS+"\",\""+SERVER_PORT+"\"",["CONNECT OK","CONNECT FAIL"],TCPCONNECTTIMEOUT);
    res = sendATcommand("AT+QIOPEN=\""+SERVER_PROTOCOL+"\",\""+SERVER_ADDRESS+"\",\""+SERVER_PORT+"\"",["CONNECT OK","CONNECT FAIL"],30)
    if(res==0):
        print("succeed")
    elif(res==1):#failure
        print("failed")
        socketClose()
    else:#timeout
        #HERE, ALSO TOO, WHEN "ERROR" RECEIVED ==> CREDIT...
        print("timeout")
        socketClose()
    return res

# socketOpen    NOT NEEDED for HTTP client data handling (upload/download)!!!!
def socketClose():
    aGsmWRITE("AT+QICLOSE\r\n")
    sleep(2.5)
    clearSInput()

