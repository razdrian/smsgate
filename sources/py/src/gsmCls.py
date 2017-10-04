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
# NAME: gsmCls.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of the GSMModem class

############################################################################################################################################

from userDefErrs import *
from gsmserialLib import *
from time import sleep
from string import replace
import threading
import RPi.GPIO as GPIO


class GSMModem:
    """
    GSM_Modem class describing the c-uGSM modem with methods to control it
    There are three main categories of methods:
        *Hardware Control methods   -> Hardware Control Methods for GSM Modem
        *Basic methods              -> Basic Methods
    *SMS_methods                    -> SMS Methods for sending and retrieving SMS
    """
    status = False
    noSMS = 0
    totSMS = 0

    def __init__(self):
        self.lock = threading.Lock()

    def powerOn(self):
        """
        if the modem is alreay up, the method raises ModemAlreadyOnError
        if it is not up, tries to power it up

        :param
            *self: GSMModem object
        :raise:
            *GPIOoutputError
            *GPIOinputError
            *SerialSetupError
            *ModemAlreadyOnError
            *ModemPowerOnError

        """
        self.refreshStat(True)
        if self.status:
            raise ModemAlreadyOnError
        else:
            try:
                GPIO.output(POWER, GPIO.LOW)
                sleep(0.1)
                GPIO.output(POWER, GPIO.HIGH)
                sleep(0.4)
                GPIO.output(POWER, GPIO.LOW)
                sleep(0.1)
            except:
                raise GPIOoutputError
        sleep(5)
        self.refreshStat(True)
        if not self.status:
            raise ModemPowerOnError


    def powerOff(self):
        """
        if the modem is alreay down, the method raises ModemAlreadyOffError
        if it is not down, tries to power it off
        :param self:
            *GSMModem object
        :raise:
            *GPIOinputError
            *SerialSetupError
            *ModemAlreadyOffError
            *ModemPowerOffError
        """

        self.refreshStat(True)
        if not self.status:
            raise ModemAlreadyOffError
        else:
            try:
                sendATcommand("AT+QPOWD", ["OK", "ERROR"], 1)
            except:
                self.status=True
                return
            else:
                self.status=False
        sleep(5)
        self.refreshStat(True)
        if self.status:
            raise ModemPowerOffError


    def restart(self):
        """
        restart the modem using powerOff() and powerOn() methods
        :param
            *self: GSMModem object
        :raise:
            *GPIOinputError
            *GPIOoutputError
            *SerialSetupError
            *ModemAlreadyOffError
            *ModemPowerOffError
        """
        self.powerOff()
        sleep(1)
        self.powerOn()


    def reset(self):
        """
        reset the modem using the RESET GPIO pin connection
        :param
            *self: GSMModem object
        :raise:
            *GPIOoutputError
        """
        try:
            GPIO.output(RESET, GPIO.LOW)
            sleep(1)
            GPIO.output(RESET, GPIO.HIGH)
            sleep(5)
        except:
            raise GPIOoutputError


    def refreshStat(self, mode):
        """
        refresh the status variable, memebr of the class
        :param self:
            *GSMModem object
            *mode:
                **True -> refresh the status using STATUS GPIO
                **False -> refresh the modem using AT command
        :raise:
            *GPIOinputError
            *SerialSetupError
        """
        if mode:
            try:
                self.status = GPIO.input(STATUS)
            except:
                traceback.print_exc()
                self.status = False
                raise GPIOinputError
        else:
            try:
                gsmModuleWrite("+++\r\n")
                gsmModuleWrite(chr(0x1B) + "\r\n")
                gsmModuleWrite("AT\r\n")
                gsmModuleWrite("ATE1\r\n")
                gsmModuleWrite("ATV1\r\n")
                clearSInput()
                clearInput()
            except:
                raise SerialSetupError
            try:
                sendATcommand("AT", ["OK", "ERROR"], 1)
            except:
                self.status=False
                return
            else:
                self.status=True




    def setup(self):
        """

        set up the GSMModem
        if a PIN in needed will raise RequestedPinError
        select text mode format, meaning that attribute are send for a command as text (eg. INBOX, READ, UNREAD) and not as numbers.
        :param
            *self: GSMModem object
        :raise:
            *PinSetupError
            *RequestedPinError
            *GSMModuleSetupError
        """
        try:
            sendATcommand("AT+QIMODE=0", ["OK", "ERROR"], 3)                            # Select TCPIP transferring mode
            sendATcommand("AT+QINDI=0", ["OK", "ERROR"], 3)                             # Set the method to handle TCPIP data
            sendATcommand("AT+QIMUX=0", ["OK", "ERROR"], 3)                             # Control whether to enable TCPIP data
            sendATcommand("AT+QIDNSIP=0", ["OK", "ERROR"], 3)                           # Connect with IP address or DNS
            sendATcommand("AT+CSCS=\"IRA\"",["OK","ERROR"],3)                           # Select TE character set to Intern Reference Alphabet
            sendATcommand("AT+CPMS=\"SM\",\"SM\",\"SM\"", ["OK", "+CMS ERROR:"], 3)     #Select storage for SMS mem1 = SM, mem2 = SM, mem3 = SM
        except:
            raise GSMModuleSetupError

        while True:
            clearInput()
            try:
                sendATcommand("AT+CPIN?", ["OK", "ERROR"], 3)   #was 5 here and abov >>>>>>>
            except:
                raise GSMModuleSetupError
            else:
                dataBuffer = getResponse()
                if (dataBuffer.find("READY")):
                    break
                else:
                    raise RequestedPinError

        sleep(1)
        while True:
            clearInput()
            try:
                sendATcommand("AT+CPBS?", ["OK", "ERROR"], 3)                           # select phonebook memory storage
            except:
                raise GSMModuleSetupError
            dataBuffer = getResponse()
            if dataBuffer.find("+CME ERROR") < 0:
                break
            sleep(0.5)

        try:
            sendATcommand("AT+CPBS=\"SM\"", ["OK", "ERROR"], 5)                         # set phonebook memory storage as SIM
            sendATcommand("AT+CMGF=1", ["OK", "ERROR"], 3)                              # select text mode format
            sendATcommand("AT+CNMI=2,0,0,0,0\r", ["OK", "ERROR"], 3)                    # SMS event reporting configuration
        except:
            raise GSMModuleSetupError
        clearInput()


    def getIMEI(self):
        """
        :param
            *self: GSMModem object
        :raise:
            *IMEIQuerryError
        :return:
            *the IMEI (Modem related identifier)
        """
        try:
            sendATcommand("AT+GSN", ["OK", "ERROR"], 3)
        except:
            raise IMEIQuerryError
        dataBuffer = getResponse()
        IMEI = dataBuffer[9:-8]
        return IMEI


    def getIMSI(self):
        """
        :param
            *self: GSMModem object
        :raise:
            *IMSIQuerryError
        :return:
            *IMSI (SIM related identifier)
        """
        clearInput()
        try:
            sendATcommand("AT+CIMI", ["OK", "ERROR"], 3)
        except:
            raise IMSIQuerryError
        else:
            dataBuffer = getResponse()
            if len(dataBuffer) > 18:
                return dataBuffer[dataBuffer.find("AT+CIMI") + 10:dataBuffer.find("OK") - 4]
            else:
                raise IMSIQuerryError


    def checkNwReg(self, timeout):
        """
        read GSM registration status from UART
        :param
            *self: GSMModem object
            *timeout: timeout value in seconds
        :raise:
            *NwRegistrationError
        """
        startTime = time.time()
        while (time.time() - startTime < timeout):
            try:
                sendATcommand("AT+CREG?", ["OK", "ERROR"], 10)
            except:
                raise NwRegistrationError
            else:
                dataBuffer = getResponse()
                if dataBuffer.find("0,1") > 0 or dataBuffer.find("0,5") > 0:
                    return
                else:
                    pass        #not yet registered, wait for timeout to pass
                sleep(0.5)
        raise NwRegistrationError


    def getSignalStat(self):
        """
        :param
            *self: GSMModem object
        :raise:
            *SignalLevelQuerryError
        :return:
            *h, signal value from 0 to 7 range
        """
        level = 0
        try:
            sendATcommand("AT+CSQ", ["OK", "ERROR"], 10)
        except:
            raise SignalLevelQuerryError
        else:
            dataBuffer = getResponse()
            startat = dataBuffer.find(": ")
            endat = dataBuffer.find(",")
            result = int(dataBuffer[startat + 2:endat])
            if result == 99:
                level = 0
            elif result > -1 and result < 8:        # -113dBm -> -99dBm
                level = 1
            elif result > 7 and result < 13:        # -99dBm -> -89dBm
                level = 2
            elif result > 12 and result < 18:       # -89dBm -> -79dBm
                level = 3
            elif result > 17 and result < 23:       # -79dBm -> -69dBm
                level = 4
            elif result > 22 and result < 28:       # -69dBm -> -59dBm
                level = 5
            elif result > 27 and result < 31:       # -59dBm -> -53dBm
                level = 6
            elif result >= 31:                      # >-53dBm
                level = 7
            return level


    def getnoSMS(self):
        """
        get the number of SMS currently stored in memory
        :param
            *self: GSM_Modem object
        :return:
            *the number of SMS currently stored in memory
        """
        return self.noSMS


    def gettotSMS(self):
        """
        get the capacity of memory
        :param
            *self: GSM_Modem object
        :return:
            *the capacity of memory stored in self.totSMS
        """
        return self.totSMS


    def getSMS(self, SMSindex):
        """
        Retrieves an SMS from SMSIndex

        :param
            *self: GSM_Modem object
            *SMSindex: The index of the SMS (range 1:20 for MT set)
        :raise:
            *GsmModuleWriteError
            *GsmModuleReadError
        :return:
            *SMS content in var SMSmessage
                **SMSmessage[0]   type(REC) READ/UNREAD
                **SMSmessage[1]   sender number
                **SMSmessage[2]   SMS date and time
                **SMSmessage[3]   SMS content(message)
        """
        global readStringLen
        SMSmessage = ["", "", "", ""]

        try:
            gsmModuleWrite("AT+CMGR=" + str(SMSindex) + "\r")
        except:
            raise GsmModuleWriteError
        try:
            recUARTdata(["OK", "ERROR"], 5, readStringLen)      # response from modem will be received in dataBuffer
        except:
            raise GsmModuleReadError
        else:
            dataBuffer = getResponse()

            processed=dataBuffer.split(",",4)
            buffer = processed[0].split("\"")
            SMSmessage[0] = replace(str(buffer[1]), "\"", "")           # type(REC) READ/UNREAD
            SMSmessage[1] = replace(str(processed[1]), "\"", "")        # sender number
            buffer = processed[3].split("\"")                           # this is junk
            buffer = processed[3].split("\"")
            SMSmessage[2] = buffer[1]                                   # date and time
            SMSmessage[3] = str(buffer[2])[2:buffer[2].find('OK')]      # message, payload

            #Logger.debug(SMSmessage[0]);
            #Logger.debug(SMSmessage[1]);
            #Logger.debug(SMSmessage[2]);
            #Logger.debug(SMSmessage[3]);
            return SMSmessage


    def sendSMS(self, phoneNumber, phoneType, message):
        """
        send a SMS according to its parameters
        :param
            self: GSM_Modem object
            phoneNumber: phone number
            phoneType:  129 for domestic format number; 145 for interantional format number
            message: SMS message to be transmited
        :raise:
            *GsmModuleWriteError
            *GsmModuleReadError
            *SendSMSError
        """
        res = 0
        try:
            gsmModuleWrite("AT+CMGS=\"" + phoneNumber + "\"," + phoneType + "\r")
        except:
            raise GsmModuleWriteError
        try:
            recUARTdata(">", "ERROR", 12)
        except:
            raise GsmModuleReadError
        message = message + chr(0x1A)                               # adding "send message char" to the message
        try:
            sendATcommand(message, ["OK", "ERROR"], 30)
        except:
            raise SendSMSError


        else:           #de scos ASAP >>>>>>
            return 0    #de scos ASAP >>>>>>


    def refreshSMSno(self):
        """
        method refreshing the current number of SMS from memory and total capacity of memory
        gets the current number of SMS from memory in var self.noSMS
        gets the total memory capacity in var self.totSMS
        :param
            *self: GSM_Modem object

        :raise:
            *SMSNumberQuerryError
        """
        errCounter = 0
        while True:
            clearInput()
            try:
                sendATcommand("AT+CPMS?", ["OK", "+CMS ERROR:"], 10)
            except:
                if errCounter < 5:
                    errCounter = errCounter + 1
                else:
                    raise SMSNumberQuerryError
            else:
                break
            sleep(0.5)

        dataBuffer = getResponse()
        try:
            processed = dataBuffer.split(",")
            self.noSMS = int(processed[1])
            self.totSMS = int(processed[2])
        except:
            raise SMSNumberQuerryError


        else:               #de scos ASAP >>>
            return 0        #de scos ASAP >>>


    def deleteSMS(self, SMSindex):
        """
        delete the SMS message from index SMSindex
        :param
            *self: GSM_Modem object
            *SMSindex: the index of the SMS message to be deleted
            *0 if succeeded and -1 for more than 5 TIMEOUT errors to communicate
        :raise:
            *DeleteSMSError
        """
        errCounter = 0
        while True:
            clearInput()
            try:
                sendATcommand("AT+CMGD=" + str(SMSindex), ["OK", "+CMS ERROR:"],10)
            except:
                if errCounter < 5:
                    errCounter = errCounter + 1
                else:
                    raise DeleteSMSError
            else:
                break
            sleep(0.5)

        return 0        #de scos ASAP >>>


    def deleteMulSMS(self, category):
        """
        :param
            *self: GSM_Modem object
            *category: can be READ,UNREAD, SENT, UNSENT, INBOX, ALL
        :raise:
            *DeleteMultipleSMSError
        """
        errCounter = 0
        while True:
            clearInput()
            try:
                #sendATcommand("AT+QMGDA=\"DEL " + "" + category + "\"", ["OK", "+CMS ERROR:"], 10)
                sendATcommand("AT+CMGD=1,4", ["OK", "+CMS ERROR:"], 10)
            except:
                if errCounter < 5:
                    errCounter = errCounter + 1
                else:
                    raise DeleteMultipleSMSError
            else:
                break
            sleep(0.5)

        return 0    #de scos ASAP >>>
