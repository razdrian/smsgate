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
# NAME: smsMth.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of SMS methods from GSMmodem class

############################################################################################################################################

from gsmserialLib import *
from string import replace


def sendSMS(self, phno, phtype, message):
    """
    send a SMS according to its parameters

    @param self: GSM_Modem object
    @param phno: phone number
    @param phtype:  129 for domestic format number; 145 for interantional format number
    @param message: SMS message to be transmited
    @return: 0 on success, 1 on failure
    """
    res = 0
    aGsmWRITE("AT+CMGS=\"" + phno + "\"," + phtype + "\r")
    res = recUARTdata(">", "ERROR", 12)
    if (res == 0):
        msg = message + chr(0x1A)  # adding "send message char" to the message
        res = sendATcommand(msg, ["OK", "ERROR"], 30)

    return res


def refreshSMSno(self):
    """
    method refreshing the current number of SMS from memory and total capacity of memory

    gets the current number of SMS from memory in var self.noSMS

    gets the total memory capacity in var self.totSMS

    @param self: GSM_Modem object
    @return: 0 for success, -1 for more than 5 TIMEOUT errors on sending command
    """
    err_count = 0
    while 1:
        clearInput()
        res = sendATcommand("AT+CPMS?", ["OK", "+CMS ERROR:"], 10)
        if (res == 0):
            break
        else:
            if err_count < 5:
                err_count += 1
            else:
                Logger.error("Error on querry number of SMS and total storage.")
                return -1
        time.sleep(0.5)
    buffd = getResponse()
    # Logger.debug(buffd)
    processed = buffd.split(",")
    try:
        self.noSMS = int(processed[1])
        self.totSMS = int(processed[2])
        return 0
    except:
        Logger.error('Could not update the number of SMSs from GSM module')
        return -1


def setSMSstorage(self, mem1, mem2, mem3):
    """
    method to set the storage for the SMS

    There are 2 physical storages in QuectelM95 chip: SIM and Mobile Equipment, each with a capacity of 10 SMS
        - Code for SIM message storage is "SM"
        - Code for Mobile Equipment is "ME"
        - Code for combining the 2 storages is "MT"

    @param self: GSM_Modem object
    @param mem1:
        - sets the memory where 'Messagees to be read and deleted' are stored
        - Storage for memory1 (SM,ME or MT)
    @param mem2:
        - parameter sets the memory where written Messages will be stored
        - Storage for memory2 (SM,ME or MT)
    @param mem3:
        - parameter sets the memory where received messages will be stored
        - Storage for memory3 (SM,ME or MT)
    @return: 0 if success, -1 for more than 5 TIMEOUT errors on sending command
    """
    err_count = 0
    while 1:
        clearInput()
        res = sendATcommand("AT+CPMS=\"" + mem1 + "\"," + "\"" + mem2 + "\",\"" + mem3 + "\"", ["OK", "+CMS ERROR:"],
                            10)
        if (res == 0):
            break
        else:
            if err_count < 5:
                err_count += 1
            else:
                Logger.error("Error trying to select the memory storages.")
                return -1
        time.sleep(0.5)
    return 0


def getSMS(self, SMSindex):
    """
    Retrieves an SMS from SMSIndex
        - SMSmessage[0]   type(REC) READ/UNREAD
        - SMSmessage[1]   sender number
        - SMSmessage[2]   SMS date and time
        - SMSmessage[3]   SMS content(message)
    @param self: GSM_Modem object
    @param SMSindex: The index of the SMS (range 1:20 for MT set)
    @return: SMS content in var SMSmessage OR -1 if failure to communicate
    """
    global sreadlen
    SMSmessage = ["", "", "", ""]

    # start read SMS
    aGsmWRITE("AT+CMGR=" + str(SMSindex) + "\r")
    recUARTdata(["OK", "ERROR"], 5, sreadlen)  # receive modem's response...in buffd
    # end read SMS

    buffd = getResponse()
    if (len(buffd) < 1):
        Logger.error("Error trying to read SMS from index " + str(SMSindex))
        return -1
   
    processed=buffd.split(",",4) 
    buff = processed[0].split("\"")
    SMSmessage[0] = replace(str(buff[1]), "\"", "")  # type(REC) READ/UNREAD
    SMSmessage[1] = replace(str(processed[1]), "\"", "")  # sender number
    buff = processed[3].split("\"")

    buff = processed[3].split("\"")

    SMSmessage[2] = buff[1]  # date and time
    SMSmessage[3] = str(buff[2])[2:buff[2].find('OK')]  # message
    # message has been processed and his content loaded into SMSmessage
    
    #Logger.info(SMSmessage[0]);
    #Logger.info(SMSmessage[1]);
    #Logger.info(SMSmessage[2]);
    #Logger.info(SMSmessage[3]);
    return SMSmessage


def deleteSMS(self, SMSindex):
    """

    delete the SMS message from index SMSindex

    @param self: GSM_Modem object
    @param SMSindex: the index of the SMS message to be deleted
    @return: 0 if succeeded and -1 for more than 5 TIMEOUT errors to communicate
    """
    err_count = 0
    while 1:
        clearInput()
        res = sendATcommand("AT+CMGD=" + str(SMSindex), ["OK", "+CMS ERROR:"],
                            10)  # //+CPMS: "SM",8,50,"SM",8,50,"SM",8,50// +CMS ERROR:
        if (res == 0):
            break
        else:
            if err_count < 5:
                err_count += 1
            else:
                Logger.error("Error trying to delete SMS index " + str(SMSindex))
                return -1
        time.sleep(0.5)
    return 0


# delete multiple SMS according to the category parameter
def deleteMulSMS(self, category):
    """

    @param self: GSM_Modem object
    @param category: can be READ,UNREAD, SENT, UNSENT, INBOX, ALL
    @return: 0 if succeeded and -1 for more than 5 TIMEOUT errors to communicate
    """
    err_count = 0
    while 1:
        clearInput()
        #res = sendATcommand("AT+QMGDA=\"DEL " + "" + category + "\"", ["OK", "+CMS ERROR:"], 10)
	res = sendATcommand("AT+CMGD=1,4", ["OK", "+CMS ERROR:"], 10)
        if (res == 0):
            break
        else:
            if err_count < 5:
                err_count += 1
            else:
                Logger.error("Error trying to delete " + str(category) + " messages.")
                return -1
        time.sleep(0.5)
    return 0

def getnoSMS(self):
    """
    get the number of SMS currently stored in memory

    @param self: GSM_Modem object
    @return: the number of SMS currently stored in memory
    """
    return self.noSMS


def gettotSMS(self):
    """
    get the capacity of memory

    @param self: GSM_Modem object
    @return: the capacity of memory stored in self.totSMS
    """
    return self.totSMS
