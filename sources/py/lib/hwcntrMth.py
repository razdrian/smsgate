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
# NAME: hwcntrMth.py
# PROJECT: SMSGate
# DESCRIPTION: This module contains only the definition of Hardware control methods for GSMclass

############################################################################################################################################

import RPi.GPIO as GPIO
from gsmserialLib import *




def refreshStat(self, mode):
    """
    refresh the status var

    @param self: GSMModem object
    @param mode: True -> refresh the status using STATUS GPIO if False -> refresh the modem using AT command
    @return: void
    """
    if mode:
        self.status = GPIO.input(STATUS)
    else:
        aGsmWRITE("+++\r\n")
        aGsmWRITE(chr(0x1B) + "\r\n")
        aGsmWRITE("AT\r\n")
        aGsmWRITE("ATE1\r\n")
        aGsmWRITE("ATV1\r\n")
        clearSInput()
        clearInput()
        res = sendATcommand("AT", ["OK", "ERROR"], 1)
        if (res > 0):
            self.status = 1
        else:
            self.status = 0


def powerOn(self):
    """
    if the modem is alreay up, the method returns

    if it is not up, tries to power it up

    if powering up fails, sends to Logger an error

    @param self: GSMModem object
    @return: 0 if success and -1 if failure
    """
    self.refreshStat(True)
    if self.status:
        Logger.info("QuectelM95 is already up!")
        return 0
    else:
        Logger.info("Trying to power on QuectelM95...")
        GPIO.output(POWER, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(POWER, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(POWER, GPIO.LOW)
	time.sleep(0.2)
    time.sleep(5)
    self.refreshStat(True)
    if self.status:
        Logger.info("QuectelM95 is now up!")
        return 0
    else:
        Logger.error("Failure powering on QuectelM95")
        return -1


def powerOff(self):
    """
    if the modem is alreay down, the method returns

    if it is not down, tries to power it off

    if powering off fails, sends to Logger an error

    @param self: GSMModem object
    @return: 0 if success and -1 for failure
    """

    self.refreshStat(True)
    if self.status:
        Logger.info("trying to shutdown QuectelM95...")
        #todo send a AT+QPOWD command
	res = sendATcommand("AT+QPOWD", ["OK", "ERROR"], 1)
    else:
        Logger.info("QuectelM95 is already down!")
        return
    time.sleep(5)
    self.refreshStat(True)
    if not self.status:
        Logger.info("QuectelM95 is now turned off ")
        #return 0
    else:
        Logger.error("failure powering off QuectelM95!")
        #return -1


def restart(self):
    """
    restart the modem using powerOff() and powerOn() methods

    @param self: GSMModem object
    @return: 0 if success and -1 for failure
    """
    # if self.powerOff() == -1:
    #     return -1
    # time.sleep(3)
    # if self.powerOn() == -1:
    #     return -1
    # return 0

    self.powerOff()
    time.sleep(3)
    self.powerOn()




def reset(self):
    """
    reset the modem using the RESET GPIO pin connection

    @param self: GSMModem object
    @return: 0 success and -1 for failure
    """
    Logger.info("trying to reset QuectelM95")
    GPIO.output(RESET, GPIO.LOW)
    time.sleep(1)
    GPIO.output(RESET, GPIO.HIGH)
    time.sleep(8)
    self.refreshStat(True)
    if not self.status:
        Logger.info("QuectelM95 is down")
        #return 0
    else:
        Logger.error("failure reset QuectelM95")
        #return -1


def hwSetup(self):
    """
    set up the GPIO pins STATUS POWER and RESET as I/O and gives them the initial value of HIGH

    @param self: GSMModem object
    @return: None
    """
    global GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
    except:
        GPIO.cleanup()  # free GPIO if there is an exception
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RESET, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setwarnings(True)


def hwRelease(self):
    """
    release all the GPIO used from GSMModem

    @param self: GSMModem object
    @return: None
    """
    try:
        GPIO.cleanup()
        Logger.info('RPi GPIO pins released successfully')
    except:
        Logger.error('Could not release RPi GPIO pins!')
