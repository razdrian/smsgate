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
# NAME: gsmserialLib.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only serial library methods used in the system

############################################################################################################################################
from globalPara import *
import time
import serial
import sys


def startSerialCom():
    """
    Start the serial communication

    Starts the serial communication and return 0 in case of success

    set the ATV uGSM module parameter to 1 to communicate in long result code format <CR><LF><verbose code><CR><LF>

    set the ATE uGSM module parameter to 1 to 'set command exho mode on'

    @return: 0 if SUCCESS -1 for ERROR
    """
    global agsm
    time.sleep(1)
    Logger.info("Open uGSM connection on /dev/ttyAMA0")

    try:
        agsm = serial.Serial("/dev/ttyAMA0", serialSpeed, timeout=1)
    except:
        Logger.error("ERROR opening uGSM connection")
        stopSerialCom()
        # agsm.open()
        # print("Try again...")
        return -1

    aGsmWRITE("+++\r\n")
    aGsmWRITE(chr(0x1B) + "\r\n")
    aGsmWRITE("AT\r\n")
    aGsmWRITE("ATE1\r\n")
    aGsmWRITE("ATV1\r\n")
    clearSInput()
    clearInput()
    return 0


def stopSerialCom():
    """
    Stop the serial communication

    Close the serial communication

    @return: 0 if SUCCESS and -1 if ERROR
    """
    global agsm
    try:
        agsm.close()
        Logger.info("Closed uGSM connection on /dev/ttyAMA0")
    except:
        Logger.error("ERROR closing SERIAL on /dev/ttyAMA0")
        return -1
    return 0


def recUARTdata(endchars, to, tm):
    """
    retrieve UART data

    Read from modem - read string is loaded in global var buffd

    @param endchars: endchars [SUCCESS STRING,FAILURE STRING]
    @param to: timeout value
    @param tm: how many chars to read (maximum) in one loop from serial
    @return: buffer length
    """
    global buffd
    global agsm
    buffd = ''
    dt = ''
    t = time.time()
    while 1:
        if time.time() - t > to:
            break
        dt = agsm.read(tm)
        buffd = buffd + dt
        if (len(buffd) > 0):
            j = 0
            for x in endchars:
                if (buffd.find(x) != -1):
                    agsm.flushInput()
                    return j
                j = j + 1
    agsm.flushInput()
    Logger.error("Unable to retrieve UART data! CDTO![" + buffd + "]")
    return -1


def sendATcommand(command, endchars, to):
    """
    Sends to the modem the  command, adding "\r\n" to the end of it

    Modem response is loaded in global var buffd

    @param command: Command to pe forwarded to the modem
    @param endchars: looking for endchars [SUCCESS STRING,FAILURE STRING]
    @param to: timeout value
    @return: 0 for SUCCESS, WILL EXIT the SYSTEM for more than ATcmdNOFRetry timeout errors in a row
    """
    global agsm
    global sreadlen

    for i in range(ATcmdNOFRetry):
        agsm.write(command + "\r\n")
        recData = recUARTdata(endchars, to, sreadlen)
        if recData != -1:
            return (recData)

    Logger.error(
        'Unable to retrieve response to %s command from QuectelM95 for %s times in a row. Sys will now exit...' % (
            command, ATcmdNOFRetry))
    sys.exit(2)


def getResponse():
    """
    @param return: buffd the global var containing the response after a sendATcommand call
    """
    #global buffd
    return buffd


def aGsmWRITE(command):
    """
    Write a command to serial without CR LF!!

    @param command: command to be written to serial
    @return: void
    """
    global agsm
    agsm.write(command)


# clear Input
def clearInput():
    """
    flush the input from serial com

    @return: void
    """
    agsm.flushInput()


def clearSInput():
    """
    @return: void
    """
    if (agsm.inWaiting()):
        agsm.read(4096)


def readline(timeout):
    """
    Read a line, which means until 0x0A (line feed) is received from UART

    @param timeout: timeout value in miliseconds
    @return: result, read line or -1 for TIMEOUT ERROR
    """
    global buffd
    cnt = 0
    c = ""
    res = 0
    buffd = ""
    startTime = 1000 * time.time()  # get the current time
    while (1):
        c = agsm.read(1)
        res = 1  # return found
        if (len(c) > 0):
            if (ord(c) == 0x0A):  # if char c is line feed
                break
            buffd = buffd + c
        if (timeout > 0 and 1000 * time.time() - startTime > timeout):
            res = -1  # timeout error
            break
    return res
