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
from userDefErrs import *
import time
import serial
import sys


def startSerialCom():
    """
    start the serial communication, if not succeeded closes the serial communication and raises an error
    set the ATV uGSM module parameter to 1 to communicate in long result code format <CR><LF><verbose code><CR><LF>
    set the ATE uGSM module parameter to 1 to 'set command exho mode on'
    :raise
       * SerialStartError
       * SerialSetupError
    """
    global gsmModule
    try:
        gsmModule = serial.Serial("/dev/ttyAMA0", serialSpeed, timeout=1)
    except:
        stopSerialCom()
        raise SerialStartError
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


def stopSerialCom():
    """
    Stop the serial communication
    :raise
        *SerialStopError
    """
    global gsmModule
    try:
        gsmModule.close()
    except:
        raise SerialStopError


def recUARTdata(endChars, timeOut, timeMany):
    """
    retrieve UART data
    Read from modem - read string is loaded in global var dataBuffer
    :param
        *endChars: endchars [SUCCESS STRING,FAILURE STRING]
        *timeOut: timeout value
        *timeMany: how many chars to read (maximum) in one loop from serial
    :return:
        *ONLY the buffer length
    :raise
        *SerialRecError
    """
    global dataBuffer
    global gsmModule
    dataBuffer = ''
    t = time.time()
    while 1:
        if time.time() - t > timeOut:
            break
        dataBuffer = dataBuffer + gsmModule.read(timeMany)
        if (len(dataBuffer) > 0):
            j = 0
            for x in endChars:
                if dataBuffer.find(x) != -1:
                    gsmModule.flushInput()
                    return j
                j = j + 1
    gsmModule.flushInput()
    raise SerialRecError


def sendATcommand(command, endChars, timeOut):
    """
    Sends to the modem the  command, adding "\r\n" to the end of it
    Modem response is loaded in global var dataBuffer
    :param
        *command: Command to pe forwarded to the modem
        *endChars: looking for endchars [SUCCESS STRING,FAILURE STRING]
        *timeOut: timeout value
    :raise:
        *SerialCommWriteError
        *SerialCommReadError
    """
    global gsmModule
    global readStringLen

    for i in range(ATcmdNOFRetry):
        try:
            gsmModule.write(command + "\r\n")
        except:
            raise SerialCommWriteError
        try:
            recData = recUARTdata(endChars, timeOut, readStringLen)
        except:
            raise SerialCommReadError
        else:
            return recData

    raise SerialCommFatalError


def getResponse():
    """
    :return:
        *dataBuffer the global var containing the response after a sendATcommand call
    """
    return dataBuffer


def gsmModuleWrite(command):
    """
    Write a command to serial without addind CR LF!!
    :param
        *command: command to be written to serial
    """
    global gsmModule
    gsmModule.write(command)


def clearInput():
    """
    flush the input from serial communication
    """
    gsmModule.flushInput()


def clearSInput():
    """
    """
    if (gsmModule.inWaiting()):
        gsmModule.read(4096)


def readline(timeout):
    """
    Reads a line, which means until 0x0A (line feed) is received from UART
    :param
        *timeout: timeout value in milliseconds
    :raise
        *SerialReadLineError
    """
    global dataBuffer
    dataBuffer = ""
    startTime = 1000 * time.time()      # get the current time
    while (1):
        c = gsmModule.read(1)
        if (len(c) > 0):
            if (ord(c) == 0x0A):        # if char c is line feed
                break
            dataBuffer = dataBuffer + c
        if (timeout > 0 and 1000 * time.time() - startTime > timeout):
            raise SerialReadLineError
            break
