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
# NAME: SerialCOM.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains SerialCOM class definition used in the system to communicate with the GSMModule

############################################################################################################################################

from globalPara import *
from Errors import *

import time
import serial
import sys
import traceback

class SerialCOM:
    def __init__(self):
        pass


    def startConnection(self):
        """
        start the serial communication, if not succeeded closes the serial communication and raises an error
        set the ATV uGSM module parameter to 1 to communicate in long result code format <CR><LF><verbose code><CR><LF>
        set the ATE uGSM module parameter to 1 to 'set command exho mode on'
        :raise
           * SerialStartError
           * SerialSetupError
        """
        try:
            self.connection = serial.Serial("/dev/ttyAMA0", serialSpeed, timeout=1)
        except:
            self.stopConnection()
            raise SerialStartError
        else:
            try:
                self.connection.write("+++\r\n")
                self.connection.write(chr(0x1B) + "\r\n")
                self.connection.write("AT\r\n")
                self.connection.write("ATE1\r\n")
                self.connection.write("ATV1\r\n")
                self.clearSInput()
                self.clearInput()
            except:
                raise SerialSetupError

            self.clearSInput()
            self.clearInput()


    def stopConnection(self):
        """
        Stop the serial communication
        :raise
            *SerialStopError
        """
        try:
            self.connection.close()
        except:
            raise SerialStopError


    def retrieveData(self, endChars, timeOut):
        """
        retrieve UART data
        Read from modem - read string is loaded in global var dataBuffer
        :param
            *endChars: endchars [SUCCESS STRING,FAILURE STRING]
            *timeOut: timeout value
            *timeMany: how many chars to read (maximum) in one loop from serial
        :raise
            *SerialRecError
        """
        self.dataBuffer = ''
        timestamp = time.time()
        while True:
            if time.time() - timestamp > timeOut:
                break
            try:
                self.dataBuffer = self.dataBuffer + self.connection.read()
            except:
                raise SerialRecError
            if self.dataBuffer:
                for endChar in endChars:
                    if endChar in self.dataBuffer:
                        self.connection.flushInput()
                        return
        self.connection.flushInput()
        raise SerialRecError


    def sendATCommand(self, command, endChars, timeOut):
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
            *SerialRecError
        """
        for i in range(ATcmdNOFRetry):
            try:
                self.connection.write(command + "\r\n")
            except:
                raise SerialCommWriteError
            try:
                self.retrieveData(endChars, timeOut)
            except:
                raise SerialCommReadError
            else:
                return
        raise SerialCommFatalError


    def clearInput(self):
        """
        flush the input from serial communication
        """
        self.connection.flushInput()


    def clearSInput(self):
        """
        """
        if (self.connection.inWaiting()):
            self.connection.read(4096)


    def readLine(self, timeout):
        """
        Reads a line, which means until 0x0A (line feed) is received from UART
        :param
            *timeout: timeout value in milliseconds
        :raise
            *SerialReadLineError
        """
        self.dataBuffer = ''
        timestamp = time.time()
        while (True):
            char = self.connection.read()
            if char:
                if ord(char) == 0x0A:        # if char is line feed
                    break
                self.dataBuffer = self.dataBuffer + char
            if (timeout > 0 and time.time() - timestamp > timeout):
                raise SerialReadLineError


serialCOM = SerialCOM()
