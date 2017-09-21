############################################################################################################################################
# COPYRIGHT (C) 2016 Razvan Petre
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

# This library is based on code developed by Dragos Iosub, Bucharest 2015. http://itbrainpower.net,original code link below:
# http://itbrainpower.net/micro-GSM-shield-module-cuGSM/GSM-micro-shield-board-module-RaspberryPI-Arduino-c-uGSM-features-code-examples
#
# NAME: basicMth.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of Basic methods from GSMmodem class

############################################################################################################################################


from gsmserialLib import *


def setup(self):
    """

    set up the GSMModem

    if a PIN in needed will break and log that the PIN must pe removed

    select text mode format, meaning that attribute are send for a command as text (eg. INBOX, READ, UNREAD) and not as numbers.

    @param self: GSMModem object
    @return: void
    """

    sendATcommand("AT+QIMODE=0", ["OK", "ERROR"], 5)    # Select TCPIP transferring mode
    sendATcommand("AT+QINDI=0", ["OK", "ERROR"], 5)     # Set the method to handle TCPIP data
    sendATcommand("AT+QIMUX=0", ["OK", "ERROR"], 5)     # Control whether to enable TCPIP data
    sendATcommand("AT+QIDNSIP=0", ["OK", "ERROR"], 5)   # Connect with IP address or DNS
    sendATcommand("AT+CSCS=\"IRA\"",["OK","ERROR"],5)   # Select TE character set to International Reference Alphabet
    Logger.info("SIM ready? no PIN checking?")
    while 1:
        clearInput()
        sendATcommand("AT+CPIN?", ["OK", "ERROR"], 5)
        buffd = getResponse()
        if (buffd.find("READY")):
            Logger.info("SIM is unlocked")
            break
        Logger.warning("SIM is locked!. Please remove the PIN verification!")
    time.sleep(1)
    Logger.info("Please wait while initializing SIM for SMS processing...")
    while 1:
        clearInput()
        sendATcommand("AT+CPBS?", ["OK", "ERROR"], 5)     # select phonebook memory storage
        buffd = getResponse()
        if (buffd.find("+CME ERROR") < 0):
            break
        time.sleep(0.5)

    sendATcommand("AT+CPBS=\"SM\"", ["OK", "ERROR"], 7)
    sendATcommand("AT+CMGF=1", ["OK", "ERROR"], 5)        # select text mode format
    sendATcommand("AT+CNMI=2,0,0,0,0\r", ["OK", "ERROR"], 5)

    clearInput()

    Logger.info("SIM initialization completed and ready to Go!")



def getIMEI(self):
    """
    @param self: GSMModem object
    @return: the IMEI (Modem related identifier)
    """
    sendATcommand("AT+GSN", ["OK", "ERROR"], 3)
    buffd = getResponse()
    IMEI = buffd[9:-8]
    return IMEI



def getIMSI(self):
    """
    @param self: GSMModem object
    @return: the IMSI (SIM related identifier)
    """
    clearInput()
    res = sendATcommand("AT+CIMI", ["OK", "ERROR"], 3)
    buffd = getResponse()
    if (res == 0 and len(buffd) > 18):
        return buffd[buffd.find("AT+CIMI") + 10:buffd.find("OK") - 4]
    else:
        return ''



def checkNwReg(self, timeout):
    """
    read GSM registration status from UART

    @param self: GSMModem object
    @param timeout: timeout value in seconds
    @return: 1 if modem is registered, -1 for TIMEOUT ERROR
    """
    startTime = time.time()
    while (time.time() - startTime < timeout):
        res = sendATcommand("AT+CREG?", ["OK", "ERROR"], 10)
        if (res == 0):
            buffd = getResponse()
            if (buffd.find("0,1") > 0 or buffd.find("0,5") > 0):  # second for Roaming registration*
                #Logger.info("QuectelM95 is registered to network")
                return 1  # modem registered, return 1
            else:
                #Logger.warning("Not yet registered...")
                pass
        time.sleep(0.5)
        return -1  # timeout->not registered



def getSignalStat(self):
    """
    @param self: GSMModem object
    @return: h, signal value from 0 to 7 range
    """
    h = 0
    res = sendATcommand("AT+CSQ", ["OK", "ERROR"], 10)
    if (res == 0):
        buffd = getResponse()
        # print buffd
        startat = buffd.find(": ")
        endat = buffd.find(",")
        # print buffd[startat+2:endat]
        res = int(buffd[startat + 2:endat])
        # print str(res)
        if (res == 99):
            h = 0
        elif (res > -1 and res < 8):  # -113dBm -> -99dBm
            h = 1
        elif (res > 7 and res < 13):  # -99dBm -> -89dBm
            h = 2
        elif (res > 12 and res < 18):  # -89dBm -> -79dBm
            h = 3
        elif (res > 17 and res < 23):  # -79dBm -> -69dBm
            h = 4
        elif (res > 22 and res < 28):  # -69dBm -> -59dBm
            h = 5
        elif (res > 27 and res < 31):  # -59dBm -> -53dBm
            h = 6
        elif (res >= 31):  # >-53dBm
            h = 7

    else:
        Logger.error("SIGNAL querry error!")
    return h



def setActiveSIM(self, SIM):
    """
    @param self: GSMModem object
    @param SIM: value of the SIM to be activated, 0 is TOP and 1 is BOTTOM
    @return: void
    """
    if (SIM < 0 or SIM > 1):
        return
    res = sendATcommand("AT+CFUN=0", ["OK", "ERROR"], 10)                   # shutdown GSM part of the modem
    time.sleep(1)                                                           # just delay a while
    Logger.info("set active SIM to: " + str(SIM))
    res = sendATcommand("AT+QDSIM=" + str(SIM), ["OK", "ERROR"], 10)        # execute change SIM cmd
    time.sleep(1)                                                           # just delay a while
    res = sendATcommand("AT+CFUN=1", ["OK", "ERROR"], 10)                   # wakeup GSM part of the modem
    self.activeSIM = SIM                                                    # load active SIM value
    time.sleep(5)                                                           # just delay a while


def getActiveSIM(self):
    """
    @param self: GSMModem object
    @return: the self.activeSIM value, 0 for TOP and 1 for BOTTOM
    """
    return self.activeSIM



